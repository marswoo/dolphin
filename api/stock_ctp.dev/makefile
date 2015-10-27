datafeeder: *.cpp *.h
	g++ -lthostmduserapiSSE -lthosttraderapiSSE -L./lib  datafeeder.cpp datafeeder.h observer.h strategy.h strategy.cpp trader.h trader.cpp util.h util.cpp -o main.bin

clean:
	rm -f main.bin
