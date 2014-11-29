for file in *
do
	iconv -f GBK -t utf8 -o "$file.new" "$file" && mv -f "$file.new" "$file"
done
