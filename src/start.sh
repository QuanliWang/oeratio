rgn2bed.py --rgn ../data/domain_anno_exons_position.rgn --out ../data/domain_anno_exons_position.bed

python rgn2vcf.py --CCDS ../data/domain_anno_exons_position.rgn --out ../data/domain_anno_exons_position.vcf

java -Xmx16g -jar /home/ec2-user/snpeff/snpEff/snpEff.jar GRCh37.75 ../data/domain_anno_exons_position.vcf > ../data/anno_domain_anno_exons_position.vcf

python extract_functional.py -v ../data/anno_domain_anno_exons_position.vcf -o ../data/fun_anno_domain_anno_exons_position.vcf

aws s3 cp ../data/anno_domain_anno_exons_position.vcf s3://bdt-quanli-bucket/
