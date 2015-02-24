#include <cmath>
#include <vector>

/*
 * Min-Max heap, as described here:
 * http://www.cs.otago.ac.nz/staffpriv/mike/Papers/MinMaxHeaps/MinMaxHeaps.pdf 
 * Also, limited size min & max heaps, implemented using a min-max heap
 */

namespace heap
{

template <typename T>
class MinMaxHeap {
private:
    void bubble_up (int index) {
        // Get the direction of this node's current level
        int dir = this->direction(index);
        // Find this node's parent
        int parent = (index - 1) / 2;
        // If this node has a parent, and they are not properly ordered
        if ( index > 0 && this->compare(index, parent) == -dir ) {
            // Swap this node and its parent
            this->swap(index, parent);
            // Continue bubbling the new parent, to fix any more disorder
            this->bubble_up_dir(parent, -dir);
        } else {
            // Bubble up this node
            this->bubble_up_dir(index, dir);
        }
    }

    void bubble_up_dir (int index, int dir) {
        // If this node has a grandparent
        if ( index > 2 ) {
            // Calculate the grandparent's index
            int grandparent = ((index - 1) / 2 - 1) / 2;
            // If this node and its grandparent are not properly ordered
            if ( this->compare(index, grandparent) == dir ) {
                // Swap this node and its grandparent
                this->swap(index, grandparent);
                // Continue bubbling up the new grandparent
                this->bubble_up_dir(grandparent, dir);
            }
        }
    }

    int direction (int index) {
        // Return -1 on a min level, and 1 on a max level
        return pow(-1, (int) floor(log2(index + 1) + 1) % 2);
    }

    int max_id () {
        // Max is at the root if the tree has one element
        int max = 0;
        // If there's more than 1 element
        if ( this->size() >= 2 ) {
            // The max must be in one of the root's children
            ++max;
            // If the root has a right child, and the right child is larger
            if ( this->size() >= 3 && this->compare(2, 1) == 1 ) {
                // The right child must be the maximum element
                ++max;
            }
        }
        return max;
    }

    inline void swap(int i, int j) {
        T tmp = this->values[i];
        this->values[i] = this->values[j];
        this->values[j] = tmp;   
    }

    void trickle_down (int index) {
        // Get the direction of this node's current level
        int dir = this->direction(index);
        // Trickle this node down in the proper direction
        this->trickle_down_dir(index, dir);
    }

    void trickle_down_dir (int index, int dir) {
        // Assume that the left child is the first child or grandchild in order
        int m = 2 * index + 1;
        int k, first_grandchild, last_grandchild;
        T tmp;

        // If this node has children
        if ( this->size() > m ) {
            // Check if the right child is before the left in the ordering
            k = m + 1;
            if ( this->size() > k && this->compare(k, m) == dir ) {
                m = k;
            }
            // Check if any grandchild is first in the ordering
            first_grandchild = 4 * index + 3;
            last_grandchild = first_grandchild + 3;
            for ( k = first_grandchild; k < this->size() && 
                 k <= last_grandchild; ++k ) {
                if ( this->compare(k, m) == dir ) {
                    m = k;
                }
            }
            // If the node is after the first (grand)child in the ordering 
            if ( this->compare(m, index) == dir ) {
                // Swap this node and its smallest descendent
                this->swap(m, index);
                // If m is a grandchild
                if ( m >= first_grandchild ) {
                    // Find m's parent
                    int parent = (m - 1) / 2;
                    // If this node and its new parent are now disordered
                    if ( this->compare(m, parent) == -dir ) {
                        // Swap them
                        this->swap(m, parent);
                    }
                    // Continue trickling down the value (now at m)
                    this->trickle_down_dir(m, dir);
                }
            }
        }
    }

protected:
    std::vector<T> values;

    int compare (int i, int j) {
        // Return 0 if i & j point to the same or equivalent values
        if ( i == j || this->values[i] == this->values[j] ) return 0;
        // Return -1 if the value at i is less than at j, and 1 if it's greater
        return pow(-1, this->values[i] < this->values[j]);
    }

public:
    MinMaxHeap () { }
    ~MinMaxHeap () { }

    T get_max () {
        // Find the index of the maximum element
        int max = this->max_id();
        // Extract the maximum value
        T ret = this->values[max];
        // Get the last value in the heap
        T last = this->values.back();
        // Remove the last value in the heap
        this->values.pop_back();
        // If the max was not the last element
        if ( this->size() > max ) {
            // Insert the previously last value where the max used to be
            this->values[max] = last;
            // Restore heap order
            this->trickle_down(max);
        }
        // Return the maximum element
        return ret;
    }

    T get_min () {
        // Extract the minimum element (always the root)
        T ret = this->values[0];
        // Get the last value in the heap
        T last = this->values.back();
        // Remove the last value in the heap
        this->values.pop_back();
        // If the heap had more than one element
        if ( this->size() ) {
            // Insert the previously last value where the min used to be
            this->values[0] = last;
            // Restore heap order
            this->trickle_down(0);
        }
        // Return the minimum element
        return ret;
    }

    void insert (T value) {
        // Add a new element to the end of the storage vector
        this->values.push_back(value);
        // Restore heap order
        this->bubble_up(this->size() - 1);
    }

    T peek_max () {
        // Return the value of the maximum element without removing it
        return this->values[this->max_id()];
    }

    T peek_min () {
        // Return the value of the minimum element without removing it
        return this->values[0];
    }

    int size () {
        // Return the number of elements in the heap
        return this->values.size();
    }
};


template <typename T>
class LimitedMaxHeap : public MinMaxHeap<T> {
private:
    unsigned capacity;

public:
    LimitedMaxHeap (unsigned capacity) {
        this->capacity = capacity;
    }
    ~LimitedMaxHeap () { }

    void insert (T value) {
        // If the heap is at capacity
        if ( this->size() >= this->capacity ) {
            // Ignore values less than the current minimum element
            if ( value <= this->peek_min() ) return;
            // Pop the minimum element off the heap
            this->get_min();
        }
        // Insert the new element into the heap
        MinMaxHeap<T>::insert(value);
    }
};


template <typename T>
class LimitedMinHeap : public MinMaxHeap<T> {
private:
    unsigned capacity;

public:
    LimitedMinHeap (unsigned capacity) {
        this->capacity = capacity;
    }
    ~LimitedMinHeap () { }

    void insert (T value) {
        // If the heap is at capacity
        if ( this->size() >= this->capacity ) {
            // Ignore values less than the current maximum element
            if ( value >= this->peek_max() ) return;
            // Pop the maximum element off the heap
            this->get_max();
        }
        // Insert the new element into the heap
        MinMaxHeap<T>::insert(value);
    }
};

}
