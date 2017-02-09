//
// Created by Shaoyan Sun on 2017/2/3.
//

#ifndef SEARCH_ENGINE_QUERY_H
#define SEARCH_ENGINE_QUERY_H

#include "Index.h"
#include <memory>
#include <unordered_map>
#include <functional>
#include <string>

struct ResultItem {
	size_t id;
	float score;
};

struct ScoreItem {
    string id;
    float score;
    inline bool operator==(const ScoreItem& other) { 
    	return false; 
    } // for converting to python list
};


class AbstractQuery {

public:
	AbstractQuery(const Index *index) : _index(index) {

    }

	virtual vector<ScoreItem> exec(
		const vector<float> &query_feature, 
		const size_t return_list_size=0) const = 0;

protected:
	const Index* _index;
};


class LinearQuery: public AbstractQuery {

public:
    LinearQuery(const Index* index) : AbstractQuery(index) {

	}

    virtual vector<ScoreItem> exec(
    	const vector<float> &query_feature, 
    	const size_t return_list_size=0) const override;

protected:
	vector<ResultItem> linear_search(const vector<float> &query_feature) const;
};


class LRSQuery: public LinearQuery {
public:
    LRSQuery(const Index* index) : LinearQuery(index) {

    }

    virtual vector<ScoreItem> exec(
            const vector<float> &query_feature,
            const size_t return_list_size=0) const override;
};


#endif //SEARCH_ENGINE_QUERY_H
