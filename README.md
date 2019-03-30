# Dobble

To just run it:

```
python main.py
```

To run the server:

```
python main.py --server
```

Then go to http://localhost:3000, to take the screenshots

Meanwhile, a tcp connection will be opened on localhost:3001 so another server can listen to it and retrieve predictions if you choose to have remote predictions

You need to use ngrok to make this tcp port public, then you can make predictions from the google collab ipynb
