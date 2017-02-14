// A program to calculate the mutual information of a dataset, using the FEAST
// toolikt rather than my python version, which will be much faster when we want
// to try out mutliple feature sets in rapid succesion. FEAST requires the
// in FORTRAN order, as [FEATURE, DATAPOINT]. This program takes a with each
// datapoint
// as a row and each feature as a column, seperated by spaces. It expects the
// file
// to be pre-discretised.

// Sample input:
// 0 0 1 2 3 2 1
// 1 1 3 2 1 1 2
// 9 9 3 8 1 3 2
#define COMPILE_C
extern "C" {
#include "FSAlgorithms.h"
}
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

enum class Error {
  ok,
  non_integer_input,
  non_equal_rows,
};

Error errcode = Error::ok;

std::vector<std::vector<unsigned int>> read_data(std::istream &input) {
  std::vector<std::vector<unsigned int>> data_vec;
  char line[256];
  int num_fields = -1;
  unsigned int num;

  while (input) {
    std::vector<unsigned int> data_row;
    input.getline(line, 256);
    auto row = std::stringstream(std::string(line));
    while (!row.eof()) {
      row >> num;
      if (row.fail()) {
        // invalid input
        errcode = Error::non_integer_input;
        return data_vec;
      }
      data_row.push_back(num);
    }
    // std::cout << data_row.size();
    if (num_fields == -1) {
      num_fields = data_row.size();
    } else if (num_fields != data_row.size()) {
      // mismatched file sizes
      errcode = Error::non_equal_rows;
      return data_vec;
    }
    data_vec.push_back(data_row);
    if (input.eof()) {
      break;
    }
  }
  return data_vec;
}

// re-arrange the input data into fortran (column major) order
std::vector<std::vector<unsigned int>>
make_fortran_order(std::vector<std::vector<unsigned int>> &data) {

  std::vector<std::vector<unsigned int>> fortran;
  int n_points = data.size();
  int n_features = data[0].size() - 1; // last column is class
  for (int i = 0; i < n_features; ++i) {
    std::vector<unsigned int> feature;
    for (int j = 0; j < n_points; ++j) {
      feature.push_back(data[j][i]);
    }
    fortran.push_back(feature);
  }
  return fortran;
}

// get the class as a seperate column
std::vector<unsigned int>
get_class(std::vector<std::vector<unsigned int>> &data) {
  int class_col = data[0].size() - 1; // last column
  std::vector<unsigned int> class_vec;
  for (auto it = data.begin(); it != data.end(); ++it) {
    class_vec.push_back((*it)[class_col]);
  }
  return class_vec;
}

// allocate a fortran array from a fortran order vector
unsigned int **unwrap_array(std::vector<std::vector<unsigned int>> &data) {
  int num_feats = data.size();
  int num_points = data[0].size();
  unsigned int **array = new unsigned int *[num_feats];
  for (int i = 0; i < num_points; ++i) {
    array[i] = data[i].data(); // returns a pointer to the vectors underlying
                               // storage: be a bit careful the vector doesn't
                               // go out of scope
  }
  return array;
}

int main() {
  std::fstream fs;
  fs.open("testinput.dat");
  auto data = read_data(fs);
  if (errcode != Error::ok) {
    std::cout << "Error" << int(errcode) << std::endl;
    return -1;
  }
  auto class_vec = get_class(data);
  auto fortran = make_fortran_order(data);

  // unsigned int** for_arr = fortran.data();
  unsigned int *class_arr = class_vec.data();
  unsigned int **data_arr = unwrap_array(fortran);

  int num_points = class_vec.size();
  int num_feats = fortran.size();

  for (int i = 0; i < num_feats; ++i) {
    for (int j = 0; j < num_points; ++j) {
      std::cout << data_arr[i][j];
    }
    std::cout << std::endl;
  }

  uint k = 2;
  unsigned int output_features[k];
  double scores[k];

  JMI(k, num_points, num_feats, data_arr, class_arr, output_features, scores);

  for (int i = 0; i < k; ++i) {
      std::cout << output_features[i];
  }
}