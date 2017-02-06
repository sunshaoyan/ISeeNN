//
// Created by Shaoyan Sun on 2017/2/3.
//

#include "Index.h"

Index::Index() : items() {

}

void Index::push_item(string id, vector<float> feature) {
    items.push_back({id, feature});
}