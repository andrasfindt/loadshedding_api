tag='2.0.0'
application_name='loadshedding_api'
docker build -t andrasfindt/"${application_name}:${tag}" .
docker push andrasfindt/"${application_name}:${tag}"
