# Improvments Docker Installation

Here I will put all the improvments so that the docker installation is optimized.
Of course all the help is welcome and this document was written with little 
knowledge of how the project works, every comment and critic is well accepted.

Also this document was though of after a brief analysis of the installation process, 
the installation process was almost concluded with success, but the way that the 
docker installation was setup was really tedious to debug. The image had to be 
rebuild more than 5 times, and each time took around 8 to 10 minutes (not sure) 
and sometimes it was to solve a something that took 10 seconds to solve.

## List of Improvments

- [ ] Improve Dockerfile cache, the steps for building the image should be 
separated. Because of the way the project is structured, it will not be possible 
to use the `installing_deps.sh` script, there's to much processes being executed 
in this file. The problem that this causes is long building times and it's harder 
to debug. 

- [ ] Also in the `installing_deps.sh` script there are at least 2 services that 
are installed that I think should be build as separate services and not in the 
image. This services are the following, Redis and kvrocks database. If more 
services are identified than should be added to this list:
    - [ ] Redis
    - [ ] kvrocks

- [ ] Of course if we remove the services from the image we need to implement them 
in the docker-compose.yaml file. Right now the docker-compose.yaml file could be 
improved. But it can be so, after all these other improvments are made.

- [ ] After separating the services we should look at the python environment and 
the packages that it uses. Some packages are being called in the requiremtents.txt 
but they are also being build in the `installing_deps.sh`. Is this really needed? 
Can we just have the packages being called in the requirements.txt? Why are we 
building the packages using apt?

- [ ] If all of these points are correct and are implemented, then it will be 
needed to create a different way of building the project and the installation 
process will not be centralized anymore (Aka: More things to maintain). So maybe 
should be a good idea to rethink the way the project is built, so that is compatible 
for docker and for bare metal installation.


- [ ] Since we are implementing docker, other tools should be explored like 
devcontainers so that we can really isolate the developing process. (If there's 
more tools that could be implemented, fell free to add to the list)
    - [ ] Devcontainers
