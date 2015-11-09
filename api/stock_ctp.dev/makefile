datafeeder: *.cpp *.h
	g++ -g -lthostmduserapiSSE -lthosttraderapiSSE -llog4cpp -L./lib  -L/usr/local/lib/ datafeeder.cpp datafeeder.h observer.h strategy_pair.h strategy_pair.cpp trader.h trader.cpp util.h util.cpp -o main.bin

clean:
	rm -f main.bin
