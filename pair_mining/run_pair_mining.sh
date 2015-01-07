source ~/.bashrc
raw_data_dir='./raw_data_20141223/'
processed_data_dir='./processed_data/'
start_date='20140101'


filelist=`ls $raw_data_dir`
for file in $filelist
do
    python prepare.py $raw_data_dir$file $processed_data_dir$file
done


python calculate_distance.py $processed_data_dir $start_date 'cos' >'cos_similarity.dat'
python calculate_distance.py $processed_data_dir $start_date 'euc' >'euc_similarity.dat'

python volatility.py $processed_data_dir $start_date >'volatility.dat'
python pair_volatility.py <'cos_similarity.dat' >'pair_volatility.dat'

python normalize.py <'cos_similarity.dat' >'cos_similarity_nor.dat'
python normalize.py <'euc_similarity.dat' >'euc_similarity_nor.dat'
python normalize.py <'pair_volatility.dat' >'pair_volatility_nor.dat'

join 'cos_similarity_nor.dat' 'euc_similarity_nor.dat' | join - 'pair_volatility_nor.dat' | python final_score.py - >'final_score.dat'

python find_candidate_pairs.py <final_score.dat >candidate_pairs.dat
