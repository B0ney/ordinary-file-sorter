if [ ! -d "./build" ]
then mkdir ./build/ ./build/configs
fi

cp ./main.py ./constants.py ./config_maker.py ./LICENSE ./README.md ./build
cp ./configs/* ./build/configs
