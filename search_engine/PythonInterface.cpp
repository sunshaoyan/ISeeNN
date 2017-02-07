//
// Created by Shaoyan Sun on 2017/2/5.
//

#include "Index.h"
#include "Query.h"

#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/python/stl_iterator.hpp>
#include <string>

using namespace boost::python;


void push_index_item(const boost::python::object& index_obj, const char* id, const boost::python::list& feat)
{
    Index* index = boost::python::extract<Index*>(index_obj);
    std::vector<float> v = std::vector<float>(boost::python::stl_input_iterator<float>(feat),
                                              boost::python::stl_input_iterator<float>());

    index->push_item(id, v);
}

vector<ScoreItem> exec_query(const boost::python::object& index_obj, const boost::python::list& query_feat, const size_t return_list_size=0)
{
    Index* index = boost::python::extract<Index*>(index_obj);
    std::vector<float> v = std::vector<float>(boost::python::stl_input_iterator<float>(query_feat),
                                              boost::python::stl_input_iterator<float>());
    Query q(index);
    return q.exec(v, return_list_size);
}

BOOST_PYTHON_FUNCTION_OVERLOADS(exec_query_overloads, exec_query, 2, 3)

BOOST_PYTHON_MODULE(search_engine)
{
    using namespace boost::python;

    class_<Index>("Index")
            .def_readonly("size", &Index::size);

    class_<ScoreItem>("ScoreItem")
            .def_readonly("id", &ScoreItem::id)
            .def_readonly("score", &ScoreItem::score);

    class_<std::vector<ScoreItem> >("ScoreList")
            .def(vector_indexing_suite<std::vector<ScoreItem> >())
            .def_readonly("count", &std::vector<ScoreItem>::size);
    using boost::python::arg;
    def("push_index_item", push_index_item,
            (arg("index"),
            arg("id"),
            arg("feat"))
    );
    def("exec_query", &exec_query, exec_query_overloads(
            (arg("index"),
            arg("query_feat"),
            arg("return_list_size")=0)
    ));
}
