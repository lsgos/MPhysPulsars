#include <chrono>
#include <cmath>
#include <fstream>
#include <random>

int main(int argc, char *argv[])
{
        unsigned int seed = std::chrono::system_clock::now().time_since_epoch().count();
        std::mt19937 engine{seed};

        std::normal_distribution<double> dmdist{800.0, 100.0};
        std::normal_distribution<double> widthdist{5.0, 1.0};
	std::normal_distribution<double> snrdist{17.5, 5.0};

	std::uniform_real_distribution<double> startdist{0.0, 900.0};

        unsigned int togenerate = atoi(argv[1]);

        std::ofstream outfile("simulationinput.dat", std::ios_base::out | std::ios_base::trunc);
        for (int igen = 0; igen < togenerate; igen++) {
        	outfile << std::max(8.0, snrdist(engine)) << " " 
			<< std::abs(dmdist(engine)) << " "
			<< std::abs(widthdist(engine)) << " "
			<< startdist(engine) << std::endl;
        }

        outfile.close();

        return 0;
}

