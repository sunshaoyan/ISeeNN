#include <iostream>
#include <chrono>
#include <ctime>
#include <random>
#include "Index.h"
#include "Query.h"
using namespace std;

int main() {

    Index index;

    random_device rnd_device;
    mt19937 mersenne_engine(rnd_device());

    std::chrono::time_point<std::chrono::system_clock> start, end;
    start = std::chrono::system_clock::now();
    for (size_t i = 0; i < 1000000; ++i) {
        //uniform_int_distribution<float> dist(0, 1);
        //auto gen = std::bind(dist, mersenne_engine);
        vector<float> vec(512);
        //generate(begin(vec), end(vec), gen);
		//string str("1a111122223333444445567890a");
        index.push_item("1a111122223333444445567890a", vec);
    }

    cout << index.size() << endl;
    end = std::chrono::system_clock::now();
//    for_each(scores.begin(), scores.end(), [](shared_ptr<ScoreItem> item){cout << item->id << ", " << item->score << endl;});
    std::chrono::duration<double> elapsed_seconds = end-start;
    std::time_t end_time = std::chrono::system_clock::to_time_t(end);
    std::cout << "finished computation at " << std::ctime(&end_time)
              << "elapsed time: " << elapsed_seconds.count() << "s\n";


    unique_ptr<AbstractQuery> q = make_unique<LRSQuery>(&index);
    vector<float> query(512);
    vector<ScoreItem> scores = q->exec(query, 300);
    return 0;
}
