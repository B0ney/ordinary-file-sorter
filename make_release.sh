if [ ! -d "./build" ]
then mkdir ./build/ ./build/configs
fi

cp ./main.py ./constants.py ./config_maker.py ./LICENSE ./build
cp ./configs/* ./build/configs

# mv ./build/main.py ./build/app.py