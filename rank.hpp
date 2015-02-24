class Ranking {
public:
    float rank;
    unsigned ID;

    Ranking() { }

    Ranking (float rank, unsigned ID) {
        this->rank = rank;
        this->ID = ID;
    }

    Ranking& operator= (Ranking arg) {
        this->rank = arg.rank;
        this->ID = arg.ID;
        return *this;
    }

};

inline bool operator< (const Ranking& lhs, const Ranking& rhs) {
    return lhs.rank < rhs.rank || (lhs.rank == rhs.rank && lhs.ID < rhs.ID);
}
inline bool operator> (const Ranking& lhs, const Ranking& rhs) {
    return rhs < lhs;
}
inline bool operator<= (const Ranking& lhs, const Ranking& rhs) {
    return ! (lhs > rhs);
}
inline bool operator>= (const Ranking& lhs, const Ranking& rhs) {
    return ! (lhs < rhs);
}
inline bool operator== (const Ranking& lhs, const Ranking& rhs) {
    return lhs.rank == rhs.rank && lhs.ID == rhs.ID;
}
inline bool operator!= (const Ranking& lhs, const Ranking& rhs) {
    return ! (lhs == rhs);
}
