from rest_framework.exceptions import APIException


class VendingMachineException(APIException):
    """
    Superclass for all exceptions with the vending machine.
    Will propagate as an HTTP 400 response if not caught
    """

    status_code = 400


class InsufficientFundsException(VendingMachineException):
    """
    Raised when the buyer does not have sufficient deposit to buy the item(s)
    """

    status_code = 406


class ProductInsufficientStockException(VendingMachineException):
    """
    Raised when the current stock of the product is less that the quantity the buyer wants to purchase
    """

    status_code = 404


class ProductOutOfStockException(VendingMachineException):
    """
    Raised when the product to buyer wants to buy a product that is out of stock
    """

    status_code = 404


class UnacceptableCoinExceptionException(VendingMachineException):
    """
    Raised when buyer deposits a coin that is not accepted by the Vending machine
    """
