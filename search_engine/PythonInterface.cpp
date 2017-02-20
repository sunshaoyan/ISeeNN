//
// Created by Shaoyan Sun on 2017/2/5.
//

#include "Index.h"
#include "Query.h"

#include <boost/python.hpp>
#include <boost/python/enum.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/python/stl_iterator.hpp>
#include <string>

enum QueryType {
    Linear,
    LRS
};


void push_index_item(const boost::python::object& index_obj, const char* id, const boost::python::list& feat)
{
    Index* index = boost::python::extract<Index*>(index_obj);
    std::vector<float> v = std::vector<float>(boost::python::stl_input_iterator<float>(feat),
                                              boost::python::stl_input_iterator<float>());

    index->push_item(id, v);
}


std::unique_ptr<AbstractQuery> get_query(const QueryType& query_type, const Index* index) {
    switch (query_type) {
        case Linear:
            return std::unique_ptr<LinearQuery>(new LinearQuery(index));
        case LRS:
            return std::unique_ptr<LRSQuery>(new LRSQuery(index));
    }
}

std::vector<ScoreItem> exec_query(const boost::python::object& index_obj,
                             const boost::python::list& query_feat,
                             const QueryType &query_type,
                             const size_t return_list_size=0)
{
    const Index* index = boost::python::extract<Index*>(index_obj);
    std::vector<float> v = std::vector<float>(boost::python::stl_input_iterator<float>(query_feat),
                                              boost::python::stl_input_iterator<float>());
    unique_ptr<AbstractQuery> q = get_query(query_type, index);
    return q->exec(v, return_list_size);
}

BOOST_PYTHON_FUNCTION_OVERLOADS(exec_query_overloads, exec_query, 3, 4)

BOOST_PYTHON_MODULE(search_engine)
{
    using namespace boost::python;
    enum_<QueryType>("QueryType")
            .value("Linear", Linear)
            .value("LRS", LRS)
            .export_values()
            ;
    class_<Index>("Index")
            .def_readonly("size", &Index::size);

    class_<ScoreItem>("ScoreItem")
            .def_readonly("id", &ScoreItem::id)
            .def_readonly("score", &ScoreItem::score);

    class_<std::vector<ScoreItem> >("ScoreList")
            .def(vector_indexing_suite<std::vector<ScoreItem> >())
            .def_readonly("count", &std::vector<ScoreItem>::size);
    using boost::python::arg;
    def("push_index_item", push_index_item,(
            arg("index"),
                    arg("id"),
                    arg("feat")

    ));
    def("exec_query", &exec_query,
        exec_query_overloads((
                arg("index"),
                arg("query_feat"),
                arg("query_type"),
                arg("return_list_size")=0
        )));
}
