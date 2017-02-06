cmake_minimum_required(VERSION 3.6)
project(search_engine)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES PythonInterface.cpp Index.cpp Index.h Query.cpp Query.h)
#set(SOURCE_FILES main.cpp Index.cpp Index.h Query.cpp Query.h)
#add_executable(search_engine ${SOURCE_FILES})

INCLUDE(FindPythonLibs)
FIND_PACKAGE(PythonInterp)
FIND_PACKAGE(PythonLibs)
if(APPLE AND ${PYTHON_VERSION_MAJOR} EQUAL 3)
    FIND_PACKAGE(Boost COMPONENTS python3)
else()
    FIND_PACKAGE(Boost COMPONENTS python)
endif()

ENABLE_TESTING()
INCLUDE_DIRECTORIES(${Boost_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIRS})
LINK_LIBRARIES(${Boost_LIBRARIES} ${PYTHON_LIBRARIES}) # Deprecated but so convenient!

PYTHON_ADD_MODULE(search_engine ${SOURCE_FILES})