//
// Created by Shaoyan Sun on 2017/2/3.
//

#include "Query.h"
#include <iostream>
#include <algorithm>
#include <numeric>
using namespace std;

vector<ScoreItem> LinearQuery::exec(const vector<float> &query_feature, const size_t return_list_size) const {
    vector<ResultItem> result_items = linear_search(query_feature);
    size_t result_size = return_list_size > 0 ? min(return_list_size, _index->size()) : return_list_size;
    vector<ScoreItem> score_items(result_size);
    for (size_t i = 0; i < result_size; ++i) {
        score_items[i] = {_index->get_id(result_items[i].id), result_items[i].score};
    }
    return score_items;
}

vector<ResultItem> LinearQuery::linear_search(const vector<float> &query_feature) const {
    const size_t index_size = _index->size();
    vector<ResultItem> result_items(index_size);
    size_t dim = query_feature.size();
    for (size_t i = 0; i < index_size; ++i) {
        const vector<float> &db_feature = _index->get_feature(i);
        float score = inner_product(query_feature.begin(), query_feature.end(), db_feature.begin(), 0.0f);
        result_items[i].id = i;
        result_items[i].score = score;
    }
    auto cmp = [](const ResultItem &a, const ResultItem &b) { return a.score > b.score; };
    sort(result_items.begin(), result_items.end(), cmp);
    return result_items;
}

vector<ScoreItem> LRSQuery::exec(const vector<float> &query_feature, const size_t return_list_size) const {
    auto result_items = linear_search(query_feature);
    size_t re_rank_number = return_list_size > 0 ? min(return_list_size, _index->size()) : return_list_size;
    result_items.resize(re_rank_number);
    size_t dimension = _index->get_feature(0).size();
    vector<float> mean_values(dimension, 0.0f);
    for (auto result_item: result_items) {
        const auto &db_feature = _index->get_feature(result_item.id);
        transform(mean_values.begin(), mean_values.end(), db_feature.begin(), mean_values.begin(), plus<float>());
    }
    for (auto &v: mean_values) { v /= re_rank_number; }
    vector<float> new_query_feature(dimension);
    transform(query_feature.begin(), query_feature.end(), mean_values.begin(), new_query_feature.begin(), minus<float>());
    float norm_query = sqrt(inner_product(new_query_feature.begin(), new_query_feature.end(), new_query_feature.begin(), 0.0f));
    for (auto &v: new_query_feature) { v /= norm_query; }
    for (auto &result_item: result_items) {
        const auto& db_feature = _index->get_feature(result_item.id);
        vector<float> new_db_feature(dimension);
        transform(db_feature.begin(), db_feature.end(), mean_values.begin(), new_db_feature.begin(), minus<float>());
        float norm_db = sqrt(inner_product(new_db_feature.begin(), new_db_feature.end(), new_db_feature.begin(), 0.0f));
        float new_score = inner_product(new_query_feature.begin(), new_query_feature.end(), new_db_feature.begin(), 0.0f) / norm_db;
        result_item.score = new_score;
    }
    auto cmp = [](const ResultItem &a, const ResultItem &b) { return a.score > b.score; };
    sort(result_items.begin(), result_items.end(), cmp);
    vector<ScoreItem> score_items(re_rank_number);
    for (size_t i = 0; i < re_rank_number; ++i) {
        score_items[i] = {_index->get_id(result_items[i].id), result_items[i].score};
    }
    return score_items;
}

