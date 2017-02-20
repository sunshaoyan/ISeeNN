cmake_minimum_required(VERSION 3.4)
project(search_engine)

set(CMAKE_CXX_STANDARD 14)

set(SOURCE_FILES PythonInterface.cpp Index.cpp Index.h Query.cpp Query.h)
#set(SOURCE_FILES main.cpp Index.cpp Index.h Query.cpp Query.h)
#add_executable(search_engine ${SOURCE_FILES})

INCLUDE(FindPythonLibs)
FIND_PACKAGE(PythonInterp)
FIND_PACKAGE(PythonLibs)
FIND_PACKAGE(Boost COMPONENTS python3)

ENABLE_TESTING()
INCLUDE_DIRECTORIES(${Boost_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIRS})
LINK_LIBRARIES(${Boost_LIBRARIES} ${PYTHON_LIBRARIES}) # Deprecated but so convenient!

PYTHON_ADD_MODULE(search_engine ${SOURCE_FILES})

INSTALL(TARGETS search_engine DESTINATION ISeeNN/search_web/)
