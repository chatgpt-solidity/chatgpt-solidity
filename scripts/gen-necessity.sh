set -e

./auditor gen evaluation/necessity/all --dataset evaluation/audited --cname2ercs=TokenERC20:20 \
--cname2ercs=MyToken:20 --cname2ercs=KIMEX:20 --cname2ercs=HBToken:20 \
--cname2ercs=CustomToken:20 --cname2ercs=ArthurStandardToken:20 --cname2ercs=KINGSGLOBAL:20 --cname2ercs=AxpireToken:20 \
--cname2ercs=xEuro:20 --cname2ercs=ZRXToken:20 --cname2ercs=IOSToken:20 \
--cname2ercs=Egypt:20 --cname2ercs=WiT:20 --cname2ercs=GEIMCOIN:20 \
--cname2ercs=BAToken:20 --cname2ercs=BITCOINSVGOLD:20 --cname2ercs=BNB:20 --cname2ercs=ArthurStandardToken:20

./auditor gen evaluation/necessity/universal --dataset evaluation/audited --gen-mode universal --cname2ercs=TokenERC20:20 \
--cname2ercs=MyToken:20 --cname2ercs=KIMEX:20 --cname2ercs=HBToken:20 \
--cname2ercs=CustomToken:20 --cname2ercs=ArthurStandardToken:20 --cname2ercs=KINGSGLOBAL:20 --cname2ercs=AxpireToken:20 \
--cname2ercs=xEuro:20 --cname2ercs=ZRXToken:20 --cname2ercs=IOSToken:20 \
--cname2ercs=Egypt:20 --cname2ercs=WiT:20 --cname2ercs=GEIMCOIN:20 \
--cname2ercs=BAToken:20 --cname2ercs=BITCOINSVGOLD:20 --cname2ercs=BNB:20 --cname2ercs=ArthurStandardToken:20

./auditor gen evaluation/necessity/fullerc --dataset evaluation/audited --gen-mode fullerc --cname2ercs=TokenERC20:20 \
--cname2ercs=MyToken:20 --cname2ercs=KIMEX:20 --cname2ercs=HBToken:20 \
--cname2ercs=CustomToken:20 --cname2ercs=ArthurStandardToken:20 --cname2ercs=KINGSGLOBAL:20 --cname2ercs=AxpireToken:20 \
--cname2ercs=xEuro:20 --cname2ercs=ZRXToken:20 --cname2ercs=IOSToken:20 \
--cname2ercs=Egypt:20 --cname2ercs=WiT:20 --cname2ercs=GEIMCOIN:20 \
--cname2ercs=BAToken:20 --cname2ercs=BITCOINSVGOLD:20 --cname2ercs=BNB:20 --cname2ercs=ArthurStandardToken:20

./auditor gen evaluation/necessity/nocm --dataset evaluation/audited --gen-mode specializednocm --cname2ercs=TokenERC20:20 \
--cname2ercs=MyToken:20 --cname2ercs=KIMEX:20 --cname2ercs=HBToken:20 \
--cname2ercs=CustomToken:20 --cname2ercs=ArthurStandardToken:20 --cname2ercs=KINGSGLOBAL:20 --cname2ercs=AxpireToken:20 \
--cname2ercs=xEuro:20 --cname2ercs=ZRXToken:20 --cname2ercs=IOSToken:20 \
--cname2ercs=Egypt:20 --cname2ercs=WiT:20 --cname2ercs=GEIMCOIN:20 \
--cname2ercs=BAToken:20 --cname2ercs=BITCOINSVGOLD:20 --cname2ercs=BNB:20 --cname2ercs=ArthurStandardToken:20

./auditor gen evaluation/necessity/noos --dataset evaluation/audited --gen-mode specializednooneshot --cname2ercs=TokenERC20:20 \
--cname2ercs=MyToken:20 --cname2ercs=KIMEX:20 --cname2ercs=HBToken:20 \
--cname2ercs=CustomToken:20 --cname2ercs=ArthurStandardToken:20 --cname2ercs=KINGSGLOBAL:20 --cname2ercs=AxpireToken:20 \
--cname2ercs=xEuro:20 --cname2ercs=ZRXToken:20 --cname2ercs=IOSToken:20 \
--cname2ercs=Egypt:20 --cname2ercs=WiT:20 --cname2ercs=GEIMCOIN:20 \
--cname2ercs=BAToken:20 --cname2ercs=BITCOINSVGOLD:20 --cname2ercs=BNB:20 --cname2ercs=ArthurStandardToken:20

./auditor gen evaluation/necessity/fullcode --dataset evaluation/audited --gen-mode fullcode --cname2ercs=TokenERC20:20 \
--cname2ercs=MyToken:20 --cname2ercs=KIMEX:20 --cname2ercs=HBToken:20 \
--cname2ercs=CustomToken:20 --cname2ercs=ArthurStandardToken:20 --cname2ercs=KINGSGLOBAL:20 --cname2ercs=AxpireToken:20 \
--cname2ercs=xEuro:20 --cname2ercs=ZRXToken:20 --cname2ercs=IOSToken:20 \
--cname2ercs=Egypt:20 --cname2ercs=WiT:20 --cname2ercs=GEIMCOIN:20 \
--cname2ercs=BAToken:20 --cname2ercs=BITCOINSVGOLD:20 --cname2ercs=BNB:20 --cname2ercs=ArthurStandardToken:20