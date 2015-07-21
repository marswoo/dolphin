wrap: *.cpp *.h *.swig
	swig -c++ -python datafeeder.swig
	gcc -I/usr/include/python2.6 -fPIC -c datafeeder_wrap.cxx
	gcc -I/usr/include/python2.6 -fPIC -c datafeeder.cpp
	g++ -shared datafeeder_wrap.o datafeeder.o -o _datafeeder.so -lsecuritymduserapi -L./api 

	echo step2
	swig -c++ -python trader.swig
	gcc -I/usr/include/python2.6 -fPIC -c trader_wrap.cxx
	gcc -I/usr/include/python2.6 -fPIC -c trader.cpp
	g++ -shared trader_wrap.o trader.o -o _trader.so -lsecuritytraderapi  -L./api

clean:
	rm -f *.o *.so *.cxx *.pyc datafeeder.py trader.py
