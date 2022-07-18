<h1 align="center">Store Management System</h1>
<h3 align="center">University project written in Python that is simulating store management system</h3>

# Table of contents:
> * [Description](#description)
>> * [Authentication](#authentication)
>> * [Admin](#admin)
>> * [Customer](#customer)
>> * [Daemon](#daemon)
>> * [Worker](#worker)
> * [How to use it](#how-to-use-it)

# Description
There are 5 part of the project:
 - [Authentication](#authentication)
 - [Admin](#admin)
 - [Customer](#customer)
 - [Daemon](#daemon)
 - [Worker](#worker)
 
## Authentication
Authentication is done via JWT tokens. There are 4 APIs:

### Register
Register user.
```
POST http://127.0.0.1:5002/register

Headers:
Content-Type: application/json

Body:
{
    "forename": "Test",
    "surname": "Test",
    "email": "test@gmail.com",
    "password": "Testpassword1",
    "is_customer": true
}

Successful Response:
{
    "message": "Registration successful!"
}

Failure Response:
{
    "message": ...
}
```

### Login
Login user and return access and refresh token.
```
POST http://127.0.0.1:5002/login

Headers:
Content-Type: application/json

Body:
{
    "email": "test@gmail.com",
    "password": "Testpassword1"
}

Successful Response:
{
    "accessToken": NEW_ACCESS_TOKEN,
    "refreshToken": NEW_REFRESH_TOKEN
}

Failure Response:
{
    "message": ...
}
```

### Refresh
Refresh the access token.
```
POST http://127.0.0.1:5002/refresh

Headers:
Authorization: Bearer YOUR_REFRESH_TOKEN

Successful Response:
{
    "accessToken": NEW_ACCESS_TOKEN
}

Failure Response:
{
    "message": ...
}
```

### Delete User
Delete the user, this API is only allowed to be called by an admin.
```
POST http://127.0.0.1:5002/delete

Headers:
Content-Type: application/json
Authorization: Bearer YOUR_ACCESS_TOKEN

Body:
{
    "email": "test@gmail.com"
}

Successful Response:
{
    "message": "Successfully deleted the user!"
}

Failure Response:
{
    "message": ...
}
```

## Admin
These are APIs for admin users. There are two APIs:

### Get Products Statistics
Get all products and return name, sold quantity and quantity that is needed to complete uncompleted orders
```
GET http://127.0.0.1:5003/productStatistics

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN

Successful Response:
{
    "statistics": [
        {             
            "name": "Product0",             
            "sold": 4,             
            "waiting": 1         
        },         
        {             
            "name": "Product1",             
            "sold": 12,             
            "waiting": 2         
        },         
        {            
            "name": "Product9",             
            "sold": 4,             
            "waiting": 0         
        },
        ...
    ]
}

Failure Response:
{
    "message": ...
}
```

### Get Categories Statistics
Get categories sorted descending by sold products.
```
GET http://127.0.0.1:5003/categoryStatistics

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN

Successful Response:
{
    "statistics": [
        "Category1",         
        "Category0",         
        "Category2",        
        "Category3",         
        "Category4",         
        "Category5",         
        "Category6",
        ...
    ]
}

Failure Response:
{
    "message": ...
}
```

## Customer
These are APIs for customer users. There are 3 APIs:

### Search Products
This API searches for all products and categories. Query params are optional. 
It returns:
- categories which name contains `category` param and has atleast one product which name contains `name` param 
- products which name contains `name` param and has atleast one category which name contains `category` param
```
GET http://127.0.0.1:5001/search

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN

Query params:
- name (product name)
- category (category name)

Successful Response:
{
    "categories": [ 
        "Category2", 
        "Category1", 
        ... 
    ], 
    "products": [ 
        { 
            "categories": [ 
                "Category1", 
                "Category2", 
                ... 
            ], 
            "id": 3, 
            "name": 
            "Product2", 
            "price": 29.89, 
            "quantity": 5 
        }, 
        ... 
    ]
}

Failure Response:
{
    "message": ...
}
```

### Order products
This API order products, it requers list of ids of products and their quantity. It returns id of the order.
```
POST http://127.0.0.1:5001/order

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN

Body:
{
    "requests": [ 
        { 
            "id": 1, 
            "quantity": 2 
        }, 
        { 
            "id": 2, 
            "quantity": 3 
        }, 
        ...
    ]
}

Successful Response:
{
    "id": 1
}

Failure Response:
{
    "message": ...
}
```

### Get orders
This API returns orders for the user. It returns list of orders, each order contains list of products with their categories.
```
GET http://127.0.0.1:5001/status

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN

Successful Response:
{
    "orders": [ 
        { 
            "products": [ 
                { 
                    "categories": [ 
                        "Category0", 
                        ... 
                    ], 
                    "name": "Product0", 
                    "price": 27.34, 
                    "received": 2, 
                    "requested": 2 
                }, 
                ... 
            ], 
            "price": 179.0, 
            "status": "COMPLETE", 
            "timestamp": "2022-05-22T20:32:17Z" 
        }, 
        ... 
    ]
}

Failure Response:
{
    "message": ...
}
```

## Daemon
This is daemon thread that doesn't have any APIs. It's only mission is to take products from Redis service, check their validity and if everything is ok add them to the DB.

## Worker
This part is for the workers of the store. It has only one API:

### Update products
This API takes `csv` file which contains products that should be updated. If file has correct data, products will be pushed to the `Redis` service.
```
GET http://127.0.0.1:5001/status

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN

Body:
- file (csv file containing products, row example: Category1|Category2|Category3,Product7, 50, 50. First part is containg categories separated by | sign, second part is the name of product, third part is the quantity and last part is the price)

Successful Response:
{
    "mesage": "Successfully pushed products on redis"
}

Failure Response:
{
    "message": ...
}
```

# How to use it

From terminal just run command `./script.sh`. It will run all commands that are needed for successfully running docker containers.
