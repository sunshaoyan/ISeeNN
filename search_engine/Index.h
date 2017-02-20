//
// Created by Shaoyan Sun on 2017/2/3.
//

#ifndef SEARCH_ENGINE_INDEX_H
#define SEARCH_ENGINE_INDEX_H

#include <string>
#include <vector>
#include <unordered_map>
using namespace std;

struct IndexItem {
    string id;
    vector<float> feature;
};

class Index {
public:
    Index();

    string get_id(size_t idx) const;
    const vector<float>& get_feature(size_t idx) const;
    size_t size() const;
    size_t dimension();

    inline void push_item(string &id, vector<float> &feature);
    inline void push_item(const char *id, vector<float> &feature);

private:
    vector<IndexItem> items;
    size_t dim;
};

inline string Index::get_id(size_t idx) const {
    return items[idx].id;
}

inline const vector<float>& Index::get_feature(size_t idx) const {
    return items[idx].feature;
}

inline size_t Index::size() const {
    return items.size();
}

inline void Index::push_item(string &id, vector<float> &feature) {
    items.push_back({move(id), move(feature)});
}

inline void Index::push_item(const char *id, vector<float> &feature) {
    items.push_back({move(string(id)), move(feature)});
}
#endif //SEARCH_ENGINE_INDEX_H
