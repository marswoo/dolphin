datafeeder: *.cpp *.h
	g++ -lthostmduserapiSSE -L./lib  datafeeder.cpp datafeeder.h observer.h strategy.h strategy.cpp trader.h trader.cpp -o main.bin

clean:
	rm -f main.bin
