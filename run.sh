docker run -it --rm -v $(pwd)/certs:/code/certs/ --name loadshedding -e SSL_ENABLED=false -e DEBUG_ENABLED=true -p 21445:21445 andrasfindt/loadshedding_api:2.0.0
