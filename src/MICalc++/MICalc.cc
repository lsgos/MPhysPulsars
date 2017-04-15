// A program to calculate the mutual information of a dataset, using the FEAST
// toolikt rather than my python version, which will be much faster when we want
// to try out mutliple feature sets in rapid succesion. FEAST requires the
// in FORTRAN order, as [FEATURE, DATAPOINT]. This program takes a with each
// datapoint as a row and each feature as a column, seperated by spaces. It
// expects the
// file to be pre-discretised.

// Sample input:
// 0 0 1 2 3 2 1
// 1 1 3 2 1 1 2
// 9 9 3 8 1 3 2

#define COMPILE_C // neccesary to make FSAlgorithms not try to import mex.h
extern "C" {
#include "FSAlgorithms.h"
#include "hellinger_measure.h"
}

#include "getopt.h"
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

// global error code
enum class Error {
  ok,
  non_integer_input,
  non_equal_rows,
};

Error errcode = Error::ok;
int errorline = 0;

// get data from file into a 2d std::vector
std::vector<std::vector<unsigned int>> read_data(std::istream &input) {
  std::vector<std::vector<unsigned int>> data_vec;
  std::string line;
  int num_fields = -1;
  unsigned int num;
  int linenum = 1;
  while (input) {
    std::vector<unsigned int> data_row;
    std::getline(input,line);
    line = line.substr(0,line.find_last_not_of(" \t\n") + 1);
    if (line == "") continue;
    auto row = std::stringstream(line);
    while (!row.eof()) {
      row >> num;
      if (row.fail()) {
        // invalid input
        errcode = Error::non_integer_input;
        errorline = linenum;
        return data_vec;
      }
      data_row.push_back(num);
    }
    if (num_fields == -1) {
      num_fields = data_row.size();
    } else if (num_fields != data_row.size()) {
      // mismatched rows
      errcode = Error::non_equal_rows;
      errorline = linenum;
      return data_vec;
    }
    data_vec.push_back(data_row);
    if (input.eof()) {
      break;
    }
    linenum++;
  }
  return data_vec;
}

// re-arrange the input data into fortran (column major) order, as required by
// FEAST
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

// allocate a plain array from a fortran order vector
unsigned int **unwrap_array(std::vector<std::vector<unsigned int>> &data) {
  int num_feats = data.size();
  int num_points = data[0].size();
  unsigned int **array = new unsigned int *[num_feats];
  for (int i = 0; i < num_feats; ++i) {
    array[i] = data[i].data();
  }
  return array;
}

void show_help() {
  std::cout << "MICalc++. Author Lewis Smith" << std::endl
            << "Ranks features in a dataset using information theory"
            << " methods, using the FEAST library." << std::endl
            << "Expects discretised data in space delimited format."
            << "Output is in the format :" << std::endl
            << std::endl
            << "FEATURE_INDEX SCORE" << std::endl
            << std::endl
            << "USAGE" << std::endl
            << '\t' << "micalc OPTIONS FILE" << std::endl
            << "OPTIONS: " << std::endl
            << '\t' << "-k INT : number of features to choose (default all)"
            << std::endl
            << '\t' << "-h     : show this message and exit" << std::endl
            << "FEATURE OPTIONS (if none provided, will calculate all measures and pretty print with titles.)" << std::endl
            << "Only one feature option will be accepted" << std::endl
            << '\t' << "--jmi  : rank using the joint mutual information" << std::endl
            << '\t' << "--mi   : rank using the mutual information" << std::endl
            << '\t' << "--hel   : rank using the hellinger distance" << std::endl;
}

int main(int argc, char *argv[]) {
  // deal with command line options
  opterr = 0;
  char *filename = nullptr;
  int c;
  unsigned int k = -1;
  int jmi_flag = 0;
  int mi_flag = 0;
  int hel_flag = 0;

  static struct option long_options[] = {
    {"jmi", no_argument, &jmi_flag, 1},
    {"mi",  no_argument, &mi_flag,  1},
    {"hel", no_argument, &hel_flag, 1},
    {0,0,0,0}, 
  };
  int flag_tot = 0;

  int option_index;
  while ((c = getopt_long(argc, argv, "hk:", long_options, &option_index)) != -1) {
    switch (c) {
    case 'h':
      show_help();
      return 0;
    case 'k':
      try {
        k = static_cast<uint>(std::stoi(optarg));
      } catch (std::exception){
        //non numeric argument to k
        show_help();
        return -1;
      }
      if (k < 1) {
        show_help();
        return -1;
      }
      break;
    case '?':
      show_help();
      return -1;
    case 'j':
      break;
    case 'm':
      break;
    case 0:
      //long option flags: they set their flags automagically
      break;
    default:
      std::cout << "hi" << std::endl;
      return -1;
    }
  }
  
  //check only one specific feature option was provided.
  flag_tot = jmi_flag + mi_flag; 
  if (flag_tot > 1 ) {
    show_help(); return -1;
  }
  // parse filename
  if (optind < (argc - 1)) {
    // only one option
    show_help();
    return -1;
  }
  std::vector<std::vector<unsigned int>> input_data;
  if (optind == argc -1) {
  	filename = argv[optind];
  	std::fstream fs;
  	fs.open(filename);
  	input_data = read_data(fs);
  	fs.close();
  } else {
  	input_data = read_data(std::cin);
  }
  	
  switch (errcode) {
  case Error::non_integer_input:
    std::cout << "Encountered non integer input in " << filename << " at line "
              << errorline
              << ", please ensure file contains only discretised input"
              << std::endl
              << "Exiting..." << std::endl;
    return 1;
  case Error::non_equal_rows:
    std::cout << "Found rows of unequal length in " << filename << " at line "
              << errorline << std::endl
              << "Exiting..." << std::endl;
    return 1;
  case Error::ok:
    break;
  }

  auto class_vec = get_class(input_data);
  auto data_vec = make_fortran_order(input_data);

  // unsigned int** for_arr = fortran.data();
  unsigned int *class_arr = class_vec.data();
  unsigned int **data_arr = unwrap_array(data_vec);

  int num_points = class_vec.size();
  int num_feats = data_vec.size();

  if (k == -1) {
    // option k not set: just do all features
    k = num_feats;
  } else if (k > num_feats) {
    std::cout << "Requested a number of features higher than the number in the "
                 "dataset"
              << std::endl
              << "Exiting...";
    return -1;
  }

  unsigned int JMI_output_features[k];
  double JMI_scores[k];

  unsigned int MIM_output_features[k];
  double MIM_scores[k];

  unsigned int H_output_features[k];
  double H_scores[k];

  
  if (flag_tot == 0) {
    //show all features with headers
    JMI(k, num_points, num_feats, data_arr, class_arr, JMI_output_features,
      JMI_scores);
    MIM(k, num_points, num_feats, data_arr, class_arr, MIM_output_features,
      MIM_scores);
    HellingerDist(k, num_points, num_feats, data_arr, class_arr, H_output_features,
      H_scores);
    std::cout << "--MI--" << std::endl;
    for (int i = 0; i < k; ++i) {
      std::cout << MIM_output_features[i] << " " << MIM_scores[i] << std::endl;
    }

    std::cout << "--JMI--" << std::endl;
    for (int i = 0; i < k; ++i) {
      std::cout << JMI_output_features[i] << " " << JMI_scores[i] << std::endl;
    }

    std::cout << "--HD--" << std::endl;
    for (int i = 0; i < k; ++i) {
      std::cout << H_output_features[i] << " " << H_scores[i] << std::endl;
    }
  } else if (jmi_flag) {
    //show only jmi, no header
     JMI(k, num_points, num_feats, data_arr, class_arr, JMI_output_features,
      JMI_scores);
    for (int i = 0; i < k; ++i) {
      std::cout << JMI_output_features[i] << " " << JMI_scores[i] << std::endl;
    }
  } else if (mi_flag) {
    //show only mi, no header
    MIM(k, num_points, num_feats, data_arr, class_arr, MIM_output_features,
      MIM_scores);
    for (int i = 0; i < k; ++i) {
      std::cout << MIM_output_features[i] << " " << MIM_scores[i] << std::endl;
    }
  }

  delete[] data_arr;
  return 0;
}