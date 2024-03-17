#[al]
alias ale="al edit"
alias alv="al view"
alias alvl="al view list"

#[dn]
alias devtunnel="echo -e 'Tunneling port \e[1;32m27017\e[0m on \e[1;32mXCRO 6.x - MongoDB\e[0m' && ssh -i ~/scripts/avconnect/av.pem -L 27017:localhost:27017 ubuntu@13.126.150.28 -N"
alias dncopy="scp -i ~/scripts/avconnect/av.pem"

#[dn_pt]
alias graf="echo -e 'Tunneling port \e[1;32m3000\e[0m on \e[1;32mPT - Monitoring\e[0m' && ssh -i ~/scripts/avconnect/av.pem -L 3000:localhost:3000 ubuntu@52.66.99.55 -N"
alias jmt="/home/vaadeendra/apps/apache-jmeter-5.6.3/bin/jmeter"
alias nsb="/home/vaadeendra/apps/nosqlbooster4mongo-8.1.6.AppImage"

#[main]
alias o.zshrc="nano ~/.zshrc"
alias q="exit"
alias s.zshrc="source ~/.zshrc"

