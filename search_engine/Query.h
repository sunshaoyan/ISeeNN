//
// Created by Shaoyan Sun on 2017/2/3.
//

#ifndef SEARCH_ENGINE_QUERY_H
#define SEARCH_ENGINE_QUERY_H

#include "Index.h"
#include <memory>

struct ScoreItem {
    string id;
    float score;
    inline bool operator==(const ScoreItem& other){ return false; } // for converting to python list
};

class Query {
public:
    Query(Index* index);
    vector<ScoreItem> exec(const vector<float> &query_feature, const size_t return_list_size=0);
private:
    Index* m_index;
};


#endif //SEARCH_ENGINE_QUERY_H
