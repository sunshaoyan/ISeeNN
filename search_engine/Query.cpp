//
// Created by Shaoyan Sun on 2017/2/3.
//

#include "Query.h"
#include <iostream>

Query::Query(Index* index) : m_index(index) {

}

vector<ScoreItem> Query::exec(const vector<float> &query_feature, size_t return_list_size) {
    const size_t index_size = m_index->size();
    vector<ScoreItem> score_items(index_size);
    size_t dim = query_feature.size();
    for (size_t i = 0; i < index_size; ++i) {
        float score = 0.0f;
        const vector<float> &db_feature = m_index->get_feature(i);
        for (int j = 0; j < dim; ++j) {
            score += query_feature[j] * db_feature[j];
        }
        score_items[i].id = m_index->get_id(i);
        score_items[i].score = score;
    }
    auto cmp = [](ScoreItem &a, ScoreItem &b) { return a.score > b.score; };
    sort(score_items.begin(), score_items.end(), cmp);
    if (return_list_size > 0 && return_list_size < score_items.size()) {
        score_items.resize(return_list_size);
    }
    return score_items;
}