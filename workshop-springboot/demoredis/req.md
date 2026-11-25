# REST API :: Get user profile by id

## API spec
* GET /api/user/:id

* Response with 200
GET /api/user/1
```
{
  "id": 1,
  "name": "Leanne Graham",
  "username": "Bret",
  "email": "Sincere@april.biz",
  "address": {
    "street": "Kulas Light",
    "suite": "Apt. 556",
    "city": "Gwenborough",
    "zipcode": "92998-3874",
    "geo": {
      "lat": "-37.3159",
      "lng": "81.1496"
    }
  },
  "phone": "1-770-736-8031 x56442",
  "website": "hildegard.org",
  "company": {
    "name": "Romaguera-Crona",
    "catchPhrase": "Multi-layered client-server neural-net",
    "bs": "harness real-time e-markets"
  }
}
```

* Response with 400
{
    "message": "Input invalid"
}

* Response with 404
{
    "message": "User not found in system"
}

* Response with 500
{
    "message": "System error"
}

## Business flow
1. Client send request to GET /api/user/:id
2. API validate request's input
   * If fail, return 400
3. Check data in redis server (hostname, port, redis database in application.properties)
   3.1 if data not found, go to step 4
   3.2 return 200
4. Get data from H2 database
   4.1 if not found, return 404

