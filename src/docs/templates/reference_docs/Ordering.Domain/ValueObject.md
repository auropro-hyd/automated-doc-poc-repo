# Value Objects

Value Objects are immutable types whose equality is determined by their property values. They are used to model concepts that do not require a unique identity, such as addresses, order items, order status, payment methods, and card types.

---

## Address

**Overview:**
Represents a postal address for an order. Used to capture delivery details and ensure value-based equality for address comparison.

**Properties:**

| Property   | Description             | Mandatory |
|:---------- |:----------------------- |:---------:|
| Street     | Street name and number  | Yes       |
| City       | City name               | Yes       |
| State      | State or region         | Yes       |
| ZipCode    | Postal code             | Yes       |
| Country    | Country name            | Yes       |

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/AggregatesModel/OrderAggregate/Address.cs)

---

## OrderItem

**Overview:**
Represents an item within an order, including product details, quantity, and price. Ensures value-based equality for order item comparison.

**Properties:**

| Property    | Description               | Mandatory |
|:----------- |:------------------------- |:---------:|
| ProductId   | Unique product identifier | Yes       |
| ProductName | Name of the product       | Yes       |
| UnitPrice   | Price per unit            | Yes       |
| Quantity    | Number of units ordered   | Yes       |
| PictureUrl  | Product image URL         | No        |

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/AggregatesModel/OrderAggregate/OrderItem.cs)

---

## OrderStatus

**Overview:**
Represents the status of an order (e.g., Submitted, Paid, Shipped). Used to track and compare order states in a value-based manner.

**Properties:**

| Property | Description       | Mandatory |
|:-------- |:----------------- |:---------:|
| Id       | Status identifier | Yes       |
| Name     | Status name       | Yes       |

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/AggregatesModel/OrderAggregate/OrderStatus.cs)

---

## PaymentMethod

**Overview:**
Represents a buyer's payment method, including card details and type. Used for payment validation and value-based comparison.

**Properties:**

| Property    | Description                 | Mandatory |
|:----------- |:--------------------------- |:---------:|
| CardTypeId  | Card type identifier        | Yes       |
| CardNumber  | Card number                 | Yes       |
| Expiration  | Expiry date                 | Yes       |
| BuyerId     | Associated buyer identifier | Yes       |

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/AggregatesModel/BuyerAggregate/PaymentMethod.cs)

---

## CardType

**Overview:**
Represents the type of payment card (e.g., Visa, MasterCard). Used for categorizing payment methods and ensuring value-based equality.

**Properties:**

| Property | Description         | Mandatory |
|:-------- |:-------------------|:---------:|
| Id       | Card type identifier| Yes       |
| Name     | Card type name      | Yes       |

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/AggregatesModel/BuyerAggregate/CardType.cs)
