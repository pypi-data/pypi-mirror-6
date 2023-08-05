#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <stdio.h>
#include <emmintrin.h>
#include <assert.h>
#include "art.h"
#include "ngx-queue.h"

/**
 * Macros to manipulate pointer tags
 */
#define IS_LEAF(x) (((uintptr_t)x & 1))
#define SET_LEAF(x) ((void*)((uintptr_t)x | 1))
#define LEAF_RAW(x) ((void*)((uintptr_t)x & ~1))


/**
 * Allocates a node4,
 * initializes to zero and sets the type.
 */
static inline art_node4* alloc_node4(void) {
    art_node4* node = calloc(1, sizeof(art_node4));
    node->n.type = NODE4;
    return node;
}

/**
 * Allocates a node16,
 * initializes to zero and sets the type.
 */
static inline art_node16* alloc_node16(void) {
    art_node16* node = calloc(1, sizeof(art_node16));
    node->n.type = NODE16;
    return node;
}

/**
 * Allocates a node48,
 * initializes to zero and sets the type.
 */
static inline art_node48* alloc_node48(void) {
    art_node48* node = calloc(1, sizeof(art_node48));
    node->n.type = NODE48;
    return node;
}

/**
 * Allocates a node256,
 * initializes to zero and sets the type.
 */
static inline art_node256* alloc_node256(void) {
    art_node256* node = calloc(1, sizeof(art_node256));
    node->n.type = NODE256;
    return node;
}

/**
 * Initializes an ART tree
 * @return 0 on success.
 */
int init_art_tree(art_tree *t) {
    t->root = NULL;
    t->size = 0;
    return 0;
}

// Recursively destroys the tree
static void destroy_node(art_node *n) {
    // Break if null
    if (!n) return;

    // Special case leafs
    if (IS_LEAF(n)) {
        free(LEAF_RAW(n));
        return;
    }

    // Handle each node type
    int i;
    union {
        art_node4 *p1;
        art_node16 *p2;
        art_node48 *p3;
        art_node256 *p4;
    } p;
    switch (n->type) {
        case NODE4:
            p.p1 = (art_node4*)n;
            for (i=0;i<n->num_children;i++) {
                destroy_node(p.p1->children[i]);
            }
            break;

        case NODE16:
            p.p2 = (art_node16*)n;
            for (i=0;i<n->num_children;i++) {
                destroy_node(p.p2->children[i]);
            }
            break;

        case NODE48:
            p.p3 = (art_node48*)n;
            for (i=0;i<n->num_children;i++) {
                destroy_node(p.p3->children[i]);
            }
            break;

        case NODE256:
            p.p4 = (art_node256*)n;
            for (i=0;i<256;i++) {
                if (p.p4->children[i])
                    destroy_node(p.p4->children[i]);
            }
            break;

        default:
            abort();
    }

    // Free ourself on the way up
    free(n);
}

/**
 * Destroys an ART tree
 * @return 0 on success.
 */
int destroy_art_tree(art_tree *t) {
    destroy_node(t->root);
    return 0;
}

/**
 * Returns the size of the ART tree.
 */
extern inline uint64_t art_size(art_tree *t);

static art_node** find_child(art_node *n, unsigned char c) {
    int i, mask, bitfield;
    union {
        art_node4 *p1;
        art_node16 *p2;
        art_node48 *p3;
        art_node256 *p4;
    } p;
    switch (n->type) {
        case NODE4:
            p.p1 = (art_node4*)n;
            for (i=0;i < n->num_children; i++) {
                if (p.p1->keys[i] == c)
                    return &p.p1->children[i];
            }
            break;

        {
        __m128i cmp;
        case NODE16:
            p.p2 = (art_node16*)n;

            // Compare the key to all 16 stored keys
            cmp = _mm_cmpeq_epi8(_mm_set1_epi8(c),
                    _mm_loadu_si128((__m128i*)p.p2->keys));

            // Use a mask to ignore children that don't exist
            mask = (1 << n->num_children) - 1;
            bitfield = _mm_movemask_epi8(cmp) & mask;

            /*
             * If we have a match (any bit set) then we can
             * return the pointer match using ctz to get
             * the index.
             */
            if (bitfield)
                return &p.p2->children[__builtin_ctz(bitfield)];
            break;
        }

        case NODE48:
            p.p3 = (art_node48*)n;
            i = p.p3->keys[c];
            if (i)
                return &p.p3->children[i-1];
            break;

        case NODE256:
            p.p4 = (art_node256*)n;
            if (p.p4->children[c])
                return &p.p4->children[c];
            break;

        default:
            abort();
    }
    return NULL;
}

// Simple inlined if
static inline int min(int a, int b) {
    return (a < b) ? a : b;
}

/**
 * Returns the number of prefix characters shared between
 * the key and node.
 */
static int check_prefix(art_node *n, char *key, int key_len, int depth) {
    int max_cmp = min(min(n->partial_len, MAX_PREFIX_LEN), key_len - depth);
    int idx;
    for (idx=0; idx < max_cmp; idx++) {
        if (n->partial[idx] != key[depth+idx])
            return idx;
    }
    return idx;
}

/**
 * Checks if a leaf matches
 * @return 0 on success.
 */
static int leaf_matches(art_leaf *n, char *key, int key_len, int depth) {
    (void)depth;
    // Fail if the key lengths are different
    if (n->key_len != (uint32_t)key_len) return 1;

    // Compare the keys starting at the depth
    return memcmp(n->key, key, key_len);
}

/**
 * Searches for a value in the ART tree
 * @arg t The tree
 * @arg key The key
 * @arg key_len The length of the key
 * @return NULL if the item was not found, otherwise
 * the value pointer is returned.
 */
void* art_search(art_tree *t, char *key, int key_len) {
    art_node **child;
    art_node *n = t->root;
    int prefix_len, depth = 0;
    while (n) {
        // Might be a leaf
        if (IS_LEAF(n)) {
            n = LEAF_RAW(n);
            // Check if the expanded path matches
            if (!leaf_matches((art_leaf*)n, key, key_len, depth)) {
                return ((art_leaf*)n)->value;
            }
            return NULL;
        }

        // Bail if the prefix does not match
        if (n->partial_len) {
            prefix_len = check_prefix(n, key, key_len, depth);
            if (prefix_len != min(MAX_PREFIX_LEN, n->partial_len))
                return NULL;
            depth = depth + n->partial_len;
        }

        // Recursively search
        child = find_child(n, key[depth]);
        n = (child) ? *child : NULL;
        depth++;
    }
    return NULL;
}

// Find the minimum leaf under a node
static art_leaf* minimum(art_node *n) {
    // Handle base cases
    if (!n) return NULL;
    if (IS_LEAF(n)) return LEAF_RAW(n);

    int idx;
    switch (n->type) {
        case NODE4:
            return minimum(((art_node4*)n)->children[0]);
        case NODE16:
            return minimum(((art_node16*)n)->children[0]);
        case NODE48:
            idx=0;
            while (!((art_node48*)n)->keys[idx]) idx++;
            idx = ((art_node48*)n)->keys[idx] - 1;
            return minimum(((art_node48*)n)->children[idx]);
        case NODE256:
            idx=0;
            while (!((art_node256*)n)->children[idx]) idx++;
            return minimum(((art_node256*)n)->children[idx]);
        default:
            abort();
    }
}

// Find the maximum leaf under a node
static art_leaf* maximum(art_node *n) {
    // Handle base cases
    if (!n) return NULL;
    if (IS_LEAF(n)) return LEAF_RAW(n);

    int idx;
    switch (n->type) {
        case NODE4:
            return maximum(((art_node4*)n)->children[n->num_children-1]);
        case NODE16:
            return maximum(((art_node16*)n)->children[n->num_children-1]);
        case NODE48:
            idx=255;
            while (!((art_node48*)n)->keys[idx]) idx--;
            idx = ((art_node48*)n)->keys[idx] - 1;
            return maximum(((art_node48*)n)->children[idx]);
        case NODE256:
            idx=255;
            while (!((art_node256*)n)->children[idx]) idx--;
            return maximum(((art_node256*)n)->children[idx]);
        default:
            abort();
    }
}

/**
 * Returns the minimum valued leaf
 */
art_leaf* art_minimum(art_tree *t) {
    return minimum((art_node*)t->root);
}

/**
 * Returns the maximum valued leaf
 */
art_leaf* art_maximum(art_tree *t) {
    return maximum((art_node*)t->root);
}

static art_leaf* make_leaf(char *key, int key_len, void *value) {
    art_leaf *l = malloc(sizeof(art_leaf)+key_len);
    l->value = value;
    l->key_len = key_len;
    memcpy(l->key, key, key_len);
    return l;
}

static int longest_common_prefix(art_leaf *l1, art_leaf *l2, int depth) {
    int max_cmp = min(l1->key_len, l2->key_len) - depth;
    int idx;
    for (idx=0; idx < max_cmp; idx++) {
        if (l1->key[depth+idx] != l2->key[depth+idx])
            return idx;
    }
    return idx;
}

static void copy_header(art_node *dest, art_node *src) {
    dest->num_children = src->num_children;
    dest->partial_len = src->partial_len;
    memcpy(dest->partial, src->partial, min(MAX_PREFIX_LEN, src->partial_len));
}

static void add_child256(art_node256 *n, art_node **ref, unsigned char c, void *child) {
    (void)ref;
    n->n.num_children++;
    n->children[c] = child;
}

static void add_child48(art_node48 *n, art_node **ref, unsigned char c, void *child) {
    if (n->n.num_children < 48) {
        int pos = 0;
        while (n->children[pos]) pos++;
        n->children[pos] = child;
        n->keys[c] = pos + 1;
        n->n.num_children++;
    } else {
        art_node256 *new = alloc_node256();
        for (int i=0;i<256;i++) {
            if (n->keys[i]) {
                new->children[i] = n->children[n->keys[i] - 1];
            }
        }
        copy_header((art_node*)new, (art_node*)n);
        *ref = (art_node*)new;
        free(n);
        add_child256(new, ref, c, child);
    }
}

static void add_child16(art_node16 *n, art_node **ref, unsigned char c, void *child) {
    if (n->n.num_children < 16) {
        __m128i cmp;

        // Compare the key to all 16 stored keys
        cmp = _mm_cmplt_epi8(_mm_set1_epi8(c),
                _mm_loadu_si128((__m128i*)n->keys));

        // Use a mask to ignore children that don't exist
        unsigned mask = (1 << n->n.num_children) - 1;
        unsigned bitfield = _mm_movemask_epi8(cmp) & mask;

        // Check if less than any
        unsigned idx;
        if (bitfield) {
            idx = __builtin_ctz(bitfield);
            memmove(n->keys+idx+1,n->keys+idx,n->n.num_children-idx);
            memmove(n->children+idx+1,n->children+idx,
                    (n->n.num_children-idx)*sizeof(void*));
        } else
            idx = n->n.num_children;

        // Set the child
        n->keys[idx] = c;
        n->children[idx] = child;
        n->n.num_children++;

    } else {
        art_node48 *new = alloc_node48();

        // Copy the child pointers and populate the key map
        memcpy(new->children, n->children,
                sizeof(void*)*n->n.num_children);
        for (int i=0;i<n->n.num_children;i++) {
            new->keys[n->keys[i]] = i + 1;
        }
        copy_header((art_node*)new, (art_node*)n);
        *ref = (art_node*)new;
        free(n);
        add_child48(new, ref, c, child);
    }
}

static void add_child4(art_node4 *n, art_node **ref, unsigned char c, void *child) {
    if (n->n.num_children < 4) {
        int idx;
        for (idx=0; idx < n->n.num_children; idx++) {
            if (c < n->keys[idx]) break;
        }

        // Shift to make room
        memmove(n->keys+idx+1, n->keys+idx, n->n.num_children - idx);
        memmove(n->children+idx+1, n->children+idx,
                (n->n.num_children - idx)*sizeof(void*));

        // Insert element
        n->keys[idx] = c;
        n->children[idx] = child;
        n->n.num_children++;

    } else {
        art_node16 *new = alloc_node16();

        // Copy the child pointers and the key map
        memcpy(new->children, n->children,
                sizeof(void*)*n->n.num_children);
        memcpy(new->keys, n->keys,
                sizeof(unsigned char)*n->n.num_children);
        copy_header((art_node*)new, (art_node*)n);
        *ref = (art_node*)new;
        free(n);
        add_child16(new, ref, c, child);
    }
}

static void add_child(art_node *n, art_node **ref, unsigned char c, void *child) {
    switch (n->type) {
        case NODE4:
            return add_child4((art_node4*)n, ref, c, child);
        case NODE16:
            return add_child16((art_node16*)n, ref, c, child);
        case NODE48:
            return add_child48((art_node48*)n, ref, c, child);
        case NODE256:
            return add_child256((art_node256*)n, ref, c, child);
        default:
            abort();
    }
}

/**
 * Calculates the index at which the prefixes mismatch
 */
static int prefix_mismatch(art_node *n, char *key, int key_len, int depth) {
    int max_cmp = min(min(MAX_PREFIX_LEN, n->partial_len), key_len - depth);
    int idx;
    for (idx=0; idx < max_cmp; idx++) {
        if (n->partial[idx] != key[depth+idx])
            return idx;
    }

    // If the prefix is short we can avoid finding a leaf
    if (n->partial_len > MAX_PREFIX_LEN) {
        // Prefix is longer than what we've checked, find a leaf
        art_leaf *l = minimum(n);
        max_cmp = min(l->key_len, key_len)- depth;
        for (; idx < max_cmp; idx++) {
            if (l->key[idx+depth] != key[depth+idx])
                return idx;
        }
    }
    return idx;
}

static void* recursive_insert(art_node *n, art_node **ref, char *key, int key_len, void *value, int depth, int *old) {

    // If we are at a NULL node, inject a leaf
    if (!n) {
        *ref = (art_node*)SET_LEAF(make_leaf(key, key_len, value));
        return NULL;
    }

    // If we are at a leaf, we need to replace it with a node
    if (IS_LEAF(n)) {
        art_leaf *l = LEAF_RAW(n);

        // Check if we are updating an existing value
        if (!leaf_matches(l, key, key_len, depth)) {
            *old = 1;
            void *old_val = l->value;
            l->value = value;
            return old_val;
        }

        // New value, we must split the leaf into a node4
        art_node4 *new = alloc_node4();

        // Create a new leaf
        art_leaf *l2 = make_leaf(key, key_len, value);

        // Determine longest prefix
        int longest_prefix = longest_common_prefix(l, l2, depth);
        new->n.partial_len = longest_prefix;
        memcpy(new->n.partial, key+depth, min(MAX_PREFIX_LEN, longest_prefix));
        // Add the leafs to the new node4
        *ref = (art_node*)new;
        // Check bounds, prefix length can be equal to key length (foo and foobar)
        add_child4(new, ref,
            l->key_len > depth+longest_prefix ? l->key[depth+longest_prefix] : 0x00,
            SET_LEAF(l));
        add_child4(new, ref,
            l2->key_len > depth+longest_prefix ? l2->key[depth+longest_prefix] : 0x00,
            SET_LEAF(l2));
        return NULL;
    }

    // Check if given node has a prefix
    if (n->partial_len) {
        // Determine if the prefixes differ, since we need to split
        int prefix_diff = prefix_mismatch(n, key, key_len, depth);
        if ((uint32_t)prefix_diff >= n->partial_len) {
            depth += n->partial_len;
            goto RECURSE_SEARCH;
        }

        // Create a new node
        art_node4 *new = alloc_node4();
        *ref = (art_node*)new;
        new->n.partial_len = prefix_diff;
        memcpy(new->n.partial, n->partial, min(MAX_PREFIX_LEN, prefix_diff));

        // Adjust the prefix of the old node
        if (n->partial_len <= MAX_PREFIX_LEN) {
            add_child4(new, ref, n->partial[prefix_diff], n);
            n->partial_len -= (prefix_diff+1);
            memmove(n->partial, n->partial+prefix_diff+1,
                    min(MAX_PREFIX_LEN, n->partial_len));
        } else {
            n->partial_len -= (prefix_diff+1);
            art_leaf *l = minimum(n);
            add_child4(new, ref, l->key[depth+prefix_diff], n);
            memcpy(n->partial, l->key+depth+prefix_diff+1,
                    min(MAX_PREFIX_LEN, n->partial_len));
        }

        // Insert the new leaf
        art_leaf *l = make_leaf(key, key_len, value);
        add_child4(new, ref, key[depth+prefix_diff], SET_LEAF(l));
        return NULL;
    }

RECURSE_SEARCH:;

    // Find a child to recurse to
    art_node **child = find_child(n, key[depth]);
    if (child) {
        return recursive_insert(*child, child, key, key_len, value, depth+1, old);
    }

    // No child, node goes within us
    art_leaf *l = make_leaf(key, key_len, value);
    add_child(n, ref, key[depth], SET_LEAF(l));
    return NULL;
}

/**
 * Inserts a new value into the ART tree
 * @arg t The tree
 * @arg key The key
 * @arg key_len The length of the key
 * @arg value Opaque value.
 * @return NULL if the item was newly inserted, otherwise
 * the old value pointer is returned.
 */
void* art_insert(art_tree *t, char *key, int key_len, void *value) {
    int old_val = 0;
    void *old = recursive_insert(t->root, &t->root, key, key_len, value, 0, &old_val);
    if (!old_val) t->size++;
    return old;
}

static void remove_child256(art_node256 *n, art_node **ref, unsigned char c) {
    n->children[c] = NULL;
    n->n.num_children--;

    // Resize to a node48 on underflow, not immediately to prevent
    // trashing if we sit on the 48/49 boundary
    if (n->n.num_children == 37) {
        art_node48 *new = alloc_node48();
        *ref = (art_node*)new;
        copy_header((art_node*)new, (art_node*)n);

        int pos = 0;
        for (int i=0;i<256;i++) {
            if (n->children[i]) {
                new->children[pos] = n->children[i];
                new->keys[i] = pos + 1;
                pos++;
            }
        }
        free(n);
    }
}

static void remove_child48(art_node48 *n, art_node **ref, unsigned char c) {
    int pos = n->keys[c];
    n->keys[c] = 0;
    n->children[pos-1] = NULL;
    n->n.num_children--;

    if (n->n.num_children == 12) {
        art_node16 *new = alloc_node16();
        *ref = (art_node*)new;
        copy_header((art_node*)new, (art_node*)n);

        int child = 0;
        for (int i=0;i<256;i++) {
            pos = n->keys[i];
            if (pos) {
                new->keys[child] = i;
                new->children[child] = n->children[pos - 1];
                child++;
            }
        }
        free(n);
    }
}

static void remove_child16(art_node16 *n, art_node **ref, art_node **l) {
    int pos = l - n->children;
    memmove(n->keys+pos, n->keys+pos+1, n->n.num_children - 1 - pos);
    memmove(n->children+pos, n->children+pos+1, (n->n.num_children - 1 - pos)*sizeof(void*));
    n->n.num_children--;

    if (n->n.num_children == 3) {
        art_node4 *new = alloc_node4();
        *ref = (art_node*)new;
        copy_header((art_node*)new, (art_node*)n);
        memcpy(new->keys, n->keys, 4);
        memcpy(new->children, n->children, 4*sizeof(void*));
        free(n);
    }
}

static void remove_child4(art_node4 *n, art_node **ref, art_node **l) {
    int pos = l - n->children;
    memmove(n->keys+pos, n->keys+pos+1, n->n.num_children - 1 - pos);
    memmove(n->children+pos, n->children+pos+1, (n->n.num_children - 1 - pos)*sizeof(void*));
    n->n.num_children--;

    // Remove nodes with only a single child
    if (n->n.num_children == 1) {
        art_node *child = n->children[0];
        if (!IS_LEAF(child)) {
            // Concatenate the prefixes
            int prefix = n->n.partial_len;
            if (prefix < MAX_PREFIX_LEN) {
                n->n.partial[prefix] = n->keys[0];
                prefix++;
            }
            if (prefix < MAX_PREFIX_LEN) {
                int sub_prefix = min(child->partial_len, MAX_PREFIX_LEN - prefix);
                memcpy(n->n.partial+prefix, child->partial, sub_prefix);
                prefix += sub_prefix;
            }

            // Store the prefix in the child
            memcpy(child->partial, n->n.partial, min(prefix, MAX_PREFIX_LEN));
            child->partial_len += n->n.partial_len + 1;
        }
        *ref = child;
        free(n);
    }
}

static void remove_child(art_node *n, art_node **ref, unsigned char c, art_node **l) {
    switch (n->type) {
        case NODE4:
            return remove_child4((art_node4*)n, ref, l);
        case NODE16:
            return remove_child16((art_node16*)n, ref, l);
        case NODE48:
            return remove_child48((art_node48*)n, ref, c);
        case NODE256:
            return remove_child256((art_node256*)n, ref, c);
        default:
            abort();
    }
}

static art_leaf* recursive_delete(art_node *n, art_node **ref, char *key, int key_len, int depth) {
    // Search terminated
    if (!n) return NULL;

    // Handle hitting a leaf node
    if (IS_LEAF(n)) {
        art_leaf *l = LEAF_RAW(n);
        if (!leaf_matches(l, key, key_len, depth)) {
            *ref = NULL;
            return l;
        }
        return NULL;
    }

    // Bail if the prefix does not match
    if (n->partial_len) {
        int prefix_len = check_prefix(n, key, key_len, depth);
        if (prefix_len != min(MAX_PREFIX_LEN, n->partial_len)) {
            return NULL;
        }
        depth += n->partial_len;
    }

    // Find child node
    art_node **child = find_child(n, key[depth]);
    if (!child) return NULL;

    // If the child is leaf, delete from this node
    if (IS_LEAF(*child)) {
        art_leaf *l = LEAF_RAW(*child);
        if (!leaf_matches(l, key, key_len, depth)) {
            remove_child(n, ref, key[depth], child);
            return l;
        }
        return NULL;

    // Recurse
    }

    return recursive_delete(*child, child, key, key_len, depth+1);
}

/**
 * Deletes a value from the ART tree
 * @arg t The tree
 * @arg key The key
 * @arg key_len The length of the key
 * @return NULL if the item was not found, otherwise
 * the value pointer is returned.
 */
void* art_delete(art_tree *t, char *key, int key_len) {
    art_leaf *l = recursive_delete(t->root, &t->root, key, key_len, 0);
    if (l) {
        t->size--;
        void *old = l->value;
        free(l);
        return old;
    }
    return NULL;
}

// Recursively iterates over the tree
static int recursive_iter(art_node *n, art_callback cb, void *data) {
    // Handle base cases
    if (!n) return 0;
    if (IS_LEAF(n)) {
        art_leaf *l = LEAF_RAW(n);
        return cb(data, (const char*)l->key, l->key_len, l->value);
    }

    int idx, res;
    switch (n->type) {
        case NODE4:
            for (int i=0; i < n->num_children; i++) {
                res = recursive_iter(((art_node4*)n)->children[i], cb, data);
                if (res) return res;
            }
            break;

        case NODE16:
            for (int i=0; i < n->num_children; i++) {
                res = recursive_iter(((art_node16*)n)->children[i], cb, data);
                if (res) return res;
            }
            break;

        case NODE48:
            for (int i=0; i < 256; i++) {
                idx = ((art_node48*)n)->keys[i];
                if (!idx) continue;

                res = recursive_iter(((art_node48*)n)->children[idx-1], cb, data);
                if (res) return res;
            }
            break;

        case NODE256:
            for (int i=0; i < 256; i++) {
                if (!((art_node256*)n)->children[i]) continue;
                res = recursive_iter(((art_node256*)n)->children[i], cb, data);
                if (res) return res;
            }
            break;

        default:
            abort();
    }
    return 0;
}

/**
 * Iterates through the entries pairs in the map,
 * invoking a callback for each. The call back gets a
 * key, value for each and returns an integer stop value.
 * If the callback returns non-zero, then the iteration stops.
 * @arg t The tree to iterate over
 * @arg cb The callback function to invoke
 * @arg data Opaque handle passed to the callback
 * @return 0 on success, or the return of the callback.
 */
int art_iter(art_tree *t, art_callback cb, void *data) {
    return recursive_iter(t->root, cb, data);
}

/**
 * Checks if a leaf prefix matches
 * @return 0 on success.
 */
static int leaf_prefix_matches(art_leaf *n, char *prefix, int prefix_len) {
    // Fail if the key length is too short
    if (n->key_len < (uint32_t)prefix_len) return 1;

    // Compare the keys
    return memcmp(n->key, prefix, prefix_len);
}

/**
 * Iterates through the entries pairs in the map,
 * invoking a callback for each that matches a given prefix.
 * The call back gets a key, value for each and returns an integer stop value.
 * If the callback returns non-zero, then the iteration stops.
 * @arg t The tree to iterate over
 * @arg prefix The prefix of keys to read
 * @arg prefix_len The length of the prefix
 * @arg cb The callback function to invoke
 * @arg data Opaque handle passed to the callback
 * @return 0 on success, or the return of the callback.
 */
int art_iter_prefix(art_tree *t, char *key, int key_len, art_callback cb, void *data) {
    art_node **child;
    art_node *n = t->root;
    int prefix_len, depth = 0;
    while (n) {
        // Might be a leaf
        if (IS_LEAF(n)) {
            n = LEAF_RAW(n);
            // Check if the expanded path matches
            if (!leaf_prefix_matches((art_leaf*)n, key, key_len)) {
                art_leaf *l = (art_leaf*)n;
                return cb(data, (const char*)l->key, l->key_len, l->value);
            }
            return 0;
        }

        // If the depth matches the prefix, we need to handle this node
        if (depth == key_len) {
            art_leaf *l = minimum(n);
            if (!leaf_prefix_matches(l, key, key_len))
               return recursive_iter(n, cb, data);
            return 0;
        }

        // Bail if the prefix does not match
        if (n->partial_len) {
            prefix_len = prefix_mismatch(n, key, key_len, depth);

            // If there is no match, search is terminated
            if (!prefix_len) {
                return 0;

            // If we've matched the prefix, iterate on this node
            } else if (depth + prefix_len == key_len) {
                return recursive_iter(n, cb, data);
            }

            // if there is a full match, go deeper
            depth = depth + n->partial_len;
        }

        // Recursively search
        child = find_child(n, key[depth]);
        n = (child) ? *child : NULL;
        depth++;
    }
    return 0;
}


// Recursively copies a tree
static art_node* recursive_copy(art_node *n) {
    // Handle the NULL nodes
    if (!n) return NULL;

    // Handle leaves
    if (IS_LEAF(n)) {
        art_leaf *l = LEAF_RAW(n);
        // Copy leaf
        l = make_leaf((char *)l->key, l->key_len, l->value);
        n = (art_node*)SET_LEAF(l);
        return n;
    }

    art_nodes p;
    switch (n->type) {
        case NODE4:
            p.node4 = alloc_node4();
            copy_header((art_node*)p.node4, n);
            memcpy(p.node4->keys, ((art_node4*)n)->keys, 4);
            for (int i=0; i < n->num_children; i++) {
                p.node4->children[i] = recursive_copy(((art_node4*)n)->children[i]);
            }
            return (art_node*)p.node4;

        case NODE16:
            p.node16 = alloc_node16();
            copy_header((art_node*)p.node16, n);
            memcpy(p.node16->keys, ((art_node16*)n)->keys, 16);
            for (int i=0; i < n->num_children; i++) {
                p.node16->children[i] = recursive_copy(((art_node16*)n)->children[i]);
            }
            return (art_node*)p.node16;

        case NODE48:
            p.node48 = alloc_node48();
            copy_header((art_node*)p.node48, n);
            memcpy(p.node48->keys, ((art_node48*)n)->keys, 256);
            for (int i=0; i < n->num_children; i++) {
                p.node48->children[i] = recursive_copy(((art_node48*)n)->children[i]);
            }
            return (art_node*)p.node48;

        case NODE256:
            p.node256 = alloc_node256();
            copy_header((art_node*)p.node256, n);
            for (int i=0; i < 256; i++) {
                p.node256->children[i] = recursive_copy(((art_node256*)n)->children[i]);
            }
            return (art_node*)p.node256;

        default:
            abort();
    }
}

/**
 * Creates a copy of an ART tree. The two trees will
 * share the internal leaves, but will NOT share internal nodes.
 * This allows leaves to be added and deleted from each tree
 * individually. It is important that concurrent updates to
 * a given key has no well defined behavior since the leaves are
 * shared.
 * @arg dst The destination tree. Not initialized yet.
 * @arg src The source tree, must be initialized.
 * @return 0 on success.
 */
int art_copy(art_tree *dst, art_tree *src) {
    dst->size = src->size;
    dst->root = recursive_copy(src->root);
    return 0;
}

/**
 * Initializes an ART tree iterator.
 * @return Pointer to iterator or NULL.
 */
art_iterator* create_art_iterator(art_tree *tree) {
    art_iterator* iterator = malloc(sizeof(art_iterator));
    if (!iterator) {
        return NULL;
    }
    iterator->node = tree->root;
    iterator->pos = 0;
    ngx_queue_init(&iterator->queue);
    return iterator;
}

/**
 * Remove all queue's element and free memory.
 */
static void destroy_queue(ngx_queue_t *h) {
    ngx_queue_t *q;
    art_iterator *iterator;

    while(!ngx_queue_empty(h)) {
        q = ngx_queue_head(h);
        iterator = ngx_queue_data(q, art_iterator, queue);
        ngx_queue_remove(q);
        free(iterator);
    }
}

/**
 * Destroys an ART iterator.
 * @return 0 on success.
 */
int destroy_art_iterator(art_iterator *iterator) {
    destroy_queue(&iterator->queue);
    free(iterator);
    return 0;
}

// get next child of node
static inline art_node* iterator_get_child_node(art_iterator *iterator) {
    int idx;
    art_node *next, *node;
    node = iterator->node;
    next = NULL;
    switch (node->type) {
        case NODE4:
            for (; iterator->pos < node->num_children; iterator->pos++) {
                next = ((art_node4*)node)->children[iterator->pos];
                if (next) break;
            }
            break;

        case NODE16:
            for (; iterator->pos < node->num_children; iterator->pos++) {
                next = ((art_node16*)node)->children[iterator->pos];
                if (next) break;
            }
            break;

        case NODE48:
            for (; iterator->pos < 256; iterator->pos++) {
                idx = ((art_node48*)node)->keys[iterator->pos];
                if (!idx) continue;
                next = ((art_node48*)node)->children[idx-1];
                if (next) break;
            }
            break;

        case NODE256:
            for (; iterator->pos < 256; iterator->pos++) {
                next = ((art_node256*)node)->children[iterator->pos];
                if (next) break;
            }
            break;

        default:
            abort();
    }
    iterator->pos++;
    return next;
}

/**
 * Return next leaf element.
 * @return The next leaf or NULL
 */
art_leaf* art_iterator_next(art_iterator *iterator) {
    if (!iterator->node) return NULL;

    ngx_queue_t *q;
    art_iterator *current;
    art_node *node;
    do {
        q = ngx_queue_head(&iterator->queue);
        current = ngx_queue_data(q, art_iterator, queue);
        node = iterator_get_child_node(current);

        if ((node != NULL) & IS_LEAF(node)) {
            // we found leaf, return it
            return LEAF_RAW(node);
        } else if (node) {
            // we found node, go into it
            current = malloc(sizeof(art_iterator));
            current->pos = 0;
            current->node = node;
            ngx_queue_insert_tail(q, &current->queue);
        } else if (!ngx_queue_empty(&iterator->queue)) {
            // we found nothing, got to top
            ngx_queue_remove(q);
            free(current);
            continue;
        } else {
            // work is done
            return NULL;
        }

    } while(1);

    return NULL;
}
