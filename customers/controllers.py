from .models import Customer, Location, ContactPerson, Person
from licenses.models import CustomerLicense, UsedSoftwareProduct
from itertools import chain
from management_portal.constants import LIMIT
from management_portal.general import Status, SaveStatus

class CustomerController:
    """
    The 'CustomerController' manages the customer model.
    This includes things like read, save and delete functions which can be called from the view.
    """

    @staticmethod
    def get_customer_by_id(id: int):
        """
        Returns a customer for a given id.

        Parameters:
        id (int): id of the customer

        Returns:
        Customer: customer
        """
        return Customer.objects.get(id = id)
    
    @staticmethod
    def get_customer_by_customer_number(customer_number: str):
        """
        Returns a customer for a given customer number.

        Parameters:
        customer_number (str): customer number of the customer

        Returns:
        Customer: customer
        """
        return Customer.objects.get(customer_number = customer_number)

    @staticmethod
    def get_customer_names(limit: int = LIMIT) -> list:
        """
        Returns all customer names as list.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: customer names
        """
        return list(Customer.objects.all()[:limit].values('id', 'name'))

    @staticmethod
    def get_filtered_customers(word: str, contains: bool = False) -> list:
        """
        Returns the filtered customers, filtering by customer number and name.
        Pass a word to filter. You can choose to filter "contains" or "is".

        Parameters:
        word     (str) : word to filter by
        contains (bool): if contains or is

        Returns:
        list: filtered customers
        """
        if contains:
            customers_by_number = Customer.objects.filter(customer_number__icontains = word).values('id', 'customer_number', 'name')
            customers_by_name   = Customer.objects.filter(name__icontains = word).values('id', 'customer_number', 'name')
        else:
            customers_by_number = Customer.objects.filter(customer_number__iexact = word).values('id', 'customer_number', 'name')
            customers_by_name   = Customer.objects.filter(name__iexact = word).values('id', 'customer_number', 'name')

        return list(chain(customers_by_name, customers_by_number))

    @staticmethod
    def get_customers_for_each_letter() -> list:
        """
        Get customers for each letter as list of dictionaries.

        Returns:
        list: customers for each letter
        """
        customer_list = []
        for i in range(65, 91):
            char = chr(i)
            customers = list(Customer.objects.filter(name__istartswith = char).values('id', 'name'))
            obj = {
                'letter'    : char,
                'customers' : customers,
            }
            customer_list.append(obj)
        
        return customer_list
    
    @staticmethod
    def get_customer_by_location_id(location_id: int):
        """
        Returns the customer belonging to a location for a given location id.

        Parameters:
        location_id (int): id of the location

        Returns:
        Customer: customer
        """
        customer = None
        location = Location.objects.get(id = location_id)
        if location:
            customer = location.customer 

        return customer

    @staticmethod
    def read(limit: int = LIMIT) -> list:
        """
        Returns all customers.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: customers
        """
        return Customer.objects.all()[:limit]

    @staticmethod
    def save(customer_number: str, name: str, id: int = 0) -> Status:
        """
        Saves a customer.
        By giving an id it edits this customer otherwise it creates a new one.

        Parameters:
        customer_number (str): customer number
        name            (str): customer name
        id              (int): customer id if customer should been edited

        Returns:
        Status: save status
        """
        status = Status()
        if not len(customer_number):
            status.message = 'Bitte Kundennummer angeben.'
        elif len(customer_number) > 32:
            status.message = 'Kundennummer darf nur maximal 32 Zeichen lang sein.'
        elif not len(name):
            status.message = 'Bitte Name angeben.'
        elif len(name) > 64:
            status.message = 'Name darf nur maximal 64 Zeichen lang sein.'
        else:
            customers = CustomerController.read()
            for customer in customers:
                if customer_number == customer.customer_number and not id == str(customer.id):
                    status.message = 'Diese Kundennummer wird bereits verwendet.'
                    break

            if not len(status.message):
                if id:
                    status = CustomerController.edit(
                        id              = id,
                        customer_number = customer_number,
                        name            = name,
                    )
                else:
                    status = CustomerController.create(
                        customer_number = customer_number,
                        name            = name,
                    )

        return status

    @staticmethod
    def create(customer_number: str, name: str) -> Status:
        """
        Creates a customer.

        Parameters:
        customer_number (str): customer number
        name            (str): customer name

        Returns:
        Status: create status
        """
        status = Status(True, 'Der Kunde "' + name + '" wurde erfolgreich angelegt.')
        try:
            customer = Customer(
                customer_number = customer_number,
                name            = name,
            )
            customer.save()
        except:
            status.status = False
            status.message = 'Es ist ein unerwarteter Fehler aufgetreten.'
        
        return status
    
    @staticmethod
    def edit(id: int, customer_number: str, name: str) -> Status:
        """
        Edits a customer.

        Parameters:
        id              (int): customer id
        customer_number (str): customer number
        name            (str): customer name

        Returns:
        Status: edit status
        """
        status = Status(True, 'Der Kunde "' + name + '"wurde erfolgreich aktualisiert')
        try:
            customer                 = Customer.objects.get(id = id)
            customer.customer_number = customer_number
            customer.name            = name
            customer.save()
        except:
            status.status = False
            status.message = 'Der zu bearbeitende Kunde wurde nicht gefunden.'
        
        return status
    
    @staticmethod
    def delete(id: int) -> Status:
        """
        Deletes a customer with the given id.

        Parameters:
        id (int): customer id of the customer to delete

        Returns:
        Status: delete status
        """
        status = Status(False, 'Der zu löschende Kunde wurde nicht gefunden.')
        try:
            customer        = Customer.objects.get(id = id)
            customer.delete()
            status.status   = True
            status.message  = 'Der Kunde "' + customer.name + '" wurde erfolgreich gelöscht.'
        except:
            pass
        
        return status


class LocationController:
    """
    The 'LocationController' manages the location model.
    This includes things like read, save and delete functions which can be called from the view.
    """

    @staticmethod
    def get_locations_by_customer(customer_id: int, limit: int = LIMIT) -> list:
        locations = Location.objects.filter(customer_id = customer_id)

        for location in locations:
            location.persons = ContactPerson.objects.filter(location_id = location.id)

        return locations

    @staticmethod
    def get_location_names(limit: int = LIMIT) -> list:
        """
        Returns all location names as list.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: location names
        """
        return list(Location.objects.all()[:limit].values('id', 'name'))

    @staticmethod
    def get_locations_by_name(word: str, contains: bool = False) -> list:
        """
        Returns the filtered locations, filtering by name.
        Pass a word to filter. You can choose to filter "contains" or "is".

        Parameters:
        word     (str) : word to filter by
        contains (bool): if contains or is

        Returns:
        list: filtered locations
        """
        if contains:
            locations = Location.objects.filter(name__icontains = word).values('id', 'name', 'postcode', 'city')
        else:
            locations = Location.objects.filter(name__iexact = word).values('id', 'name', 'postcode', 'city')
        
        for location in locations:
            customer             = Customer.objects.get(id = location['id'])
            location['customer'] = customer.name

        return list(locations)
    
    @staticmethod
    def get_location_by_id(id: int) -> list:
        """
        Returns the location with the given id.

        Parameters:
        id (int): id of the location

        Returns:
        Location: location
        """
        return Location.objects.get(id = id)

    @staticmethod
    def save(name: str, email_address: str, phone_number: str, street: str,
        house_number: str, postcode: str, city: str, customer: int, id: int = 0) -> Status:
        """
        Saves a customer's location.

        Parameter:
        name          (str): location name
        email_address (str): email address of the location
        phone_number  (str): phone number of the location
        street        (str): street of the location's address
        house_number  (str): house number of the location's address
        postcode      (str): postcode of the location's address
        city          (str): city of the location's address
        customer      (int): id for the customer the location belongs to
        id            (int): location id if location should been edited

        Returns:
        Status: save status
        """
        status = Status()
        save_status = LocationController.__check_validity(
            name          = name,
            email_address = email_address,
            phone_number  = phone_number,
            street        = street,
            house_number  = house_number,
            postcode      = postcode,
            city          = city,
            customer      = customer,
        )
        if save_status.status:
            if id:
                status = LocationController.edit(
                    id            = id,
                    name          = name,
                    email_address = email_address,
                    phone_number  = phone_number,
                    street        = street,
                    house_number  = house_number,
                    postcode      = postcode,
                    city          = city,
                    customer      = save_status.instances['customer'],
                )
            else:
                status = LocationController.create(
                    name          = name,
                    email_address = email_address,
                    phone_number  = phone_number,
                    street        = street,
                    house_number  = house_number,
                    postcode      = postcode,
                    city          = city,
                    customer      = save_status.instances['customer'],
                )
        else:
            status.status  = save_status.status
            status.message = save_status.message
        
        return status

    @staticmethod
    def create(name: str, email_address: str, phone_number: str, street: str,
        house_number: str, postcode: str, city: str, customer) -> Status:
        """
        Creates a customer's location and used products if customer licenses existing.

        Parameter:
        name          (str)     : location name
        email_address (str)     : email address of the location
        phone_number  (str)     : phone number of the location
        street        (str)     : street of the location's address
        house_number  (str)     : house number of the location's address
        postcode      (str)     : postcode of the location's address
        city          (str)     : city of the location's address
        customer      (Customer): belonging customer

        Returns:
        Status: create status
        """
        status    = Status(True, 'Der Standort "' + name + '" wurde erfolgreich angelegt.')
        up_status = None
        try:
            location = Location(
                name          = name,
                email_address = email_address,
                phone_number  = phone_number,
                street        = street,
                house_number  = house_number,
                postcode      = postcode,
                city          = city,
                customer      = customer,
            )
            location.save()
            up_status = LocationController.__create_used_products(
                customer = customer,
                location = location,
            )
        except:
            status.status = False
            status.message = 'Es ist ein unerwarteter Fehler aufgetreten.'

        if up_status and not up_status.status:
            status.status = False
            status.message = 'Es ist ein unerwarteter Fehler aufgetreten.'

        return status

    @staticmethod
    def edit(id: int, name: str, email_address: str, phone_number: str, street: str,
        house_number: str, postcode: str, city: str, customer) -> Status:
        """
        Saves a customer's location.

        Parameter:
        id            (int)     : location id
        name          (str)     : location name
        email_address (str)     : email address of the location
        phone_number  (str)     : phone number of the location
        street        (str)     : street of the location's address
        house_number  (str)     : house number of the location's address
        postcode      (str)     : postcode of the location's address
        city          (str)     : city of the location's address
        customer      (Customer): belonging customer

        Returns:
        Status: edit status
        """
        status = Status(True, 'Der Standort "' + name + '" wurde erfolgreich aktualisiert.')

        try:
            location                = Location.objects.get(id = id)
            location.name           = name
            location.email_address  = email_address
            location.phone_number   = phone_number
            location.street         = street
            location.house_number   = house_number
            location.postcode       = postcode
            location.city           = city
            location.customer       = customer
            location.save()
        except:
            status.status = False
            status.message = 'Der zu bearbeitende Standort wurde nicht gefunden.'

        return status

    @staticmethod
    def delete(id: int) -> Status:
        """
        Deletes a location with the given id.

        Parameters:
        id (int): location id of the customer to delete

        Returns:
        Status: delete status
        """
        status = Status(False, 'Der zu löschende Standort wurde nicht gefunden.')
        try:
            location        = Location.objects.get(id = id)
            location.delete()
            status.status   = True
            status.message  = 'Der Standort "' + location.name + '" wurde erfolgreich gelöscht.'
        except:
            pass
        
        return status

    @staticmethod
    def __check_validity(name: str, email_address: str, phone_number: str, street: str,
        house_number: str, postcode: str, city: str, customer: int) -> SaveStatus:
        """
        Checks the completeness and validity of location data to save.

        Parameter:
        name          (str): location name
        email_address (str): email address of the location
        phone_number  (str): phone number of the location
        street        (str): street of the location's address
        house_number  (str): house number of the location's address
        postcode      (str): postcode of the location's address
        city          (str): city of the location's address
        customer      (int): id for the customer the location belongs to

        Returns:
        save_status: save status
        """
        instances = {
            'customer': customer,
        }
        status = SaveStatus(instances = instances)

        if not len(name):
            status.message = 'Bitte Namen angeben.'
        elif len(name) > 64:
            status.message = 'Name darf nur maximal 64 Zeichen enthalten.'
        elif not len(email_address):
            status.message = 'Bitte E-Mail-Adresse angeben.'
        elif len(email_address) > 64:
            status.message = 'E-Mail-Adresse darf nur maximal 64 Zeichen enthalten.'
        elif not len(phone_number):
            status.message = 'Bitte Telefonnummer angeben.'
        elif len(phone_number) > 64:
            status.message = 'Telefonnummer darf nur maximal 64 Zeichen enthalten.'
        elif not len(street):
            status.message = 'Bitte Straße angeben.'
        elif len(street) > 64:
            status.message = 'Straße darf nur maximal 64 Zeichen enthalten.'
        elif not len(house_number):
            status.message = 'Bitte Hausnummer angeben.'
        elif len(house_number) > 8:
            status.message = 'Hausnummer darf nur maximal 8 Zeichen enthalten.'
        elif not len(postcode):
            status.message = 'Bitte Postleitzahl (PLZ) angeben.'
        elif len(postcode) > 16:
            status.message = 'Postleitzahl (PLZ) darf nur maximal 16 Zeichen enthalten.'
        elif not len(city):
            status.message = 'Bitte Ort angeben.'
        elif len(city) > 64:
            status.message = 'Ort darf nur maximal 64 Zeichen enthalten.'
        elif not customer:
            status.message = 'Bitte Kunden zuweisen.'
        else:
            try:
                status.instances['customer'] = Customer.objects.get(id = customer)
                status.status                = True
            except:
                status.message = 'Zugewiesenes Modul nicht gefunden.'

        return status

    @staticmethod
    def __create_used_products(customer, location) -> Status:
        """
        Creates used products for given location if the given customer has customer licenses.

        Parameter:
        customer (Customer): customer to check licenses for
        location (Location): location to create used products for

        Returns:
        Status: create status
        """
        status = Status(True)
        try:
            licenses = CustomerLicense.objects.filter(customer = customer)
            for license in licenses:
                used_product = UsedSoftwareProduct(
                    location = location,
                    product  = license.module.product,
                    version  = license.module.product.version,
                )
                used_product.save()
        except:
            status.status = False
        
        return status


class ContactPersonController:
    """
    The 'ContactPersonController' manages the contact person model.
    """

    @staticmethod
    def get_contact_persons_by_name(word: str, contains: bool = False) -> list:
        """
        Returns the filtered contact persons, filtering by first name and last name.
        Pass a word to filter. You can choose to filter "contains" or "is".

        Parameters:
        word     (str) : word to filter by
        contains (bool): if contains or is

        Returns:
        list: filtered contact persons
        """
        words = word.split(' ')

        if contains:
            if len(words) == 2:
                contacts_one = ContactPerson.objects.filter(first_name__icontains = words[0], last_name__icontains = words[1]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts_two = ContactPerson.objects.filter(first_name__icontains = words[1], last_name__icontains = words[0]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts     = list(chain(contacts_one, contacts_two))
            elif len(words) == 3:
                contacts_one = ContactPerson.objects.filter(first_name__icontains = words[0] + words[1], last_name__icontains = words[2]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts_two = ContactPerson.objects.filter(first_name__icontains = words[1] + words[2], last_name__icontains = words[0]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts     = list(chain(contacts_one, contacts_two))
            else:
                contacts_by_first_name = ContactPerson.objects.filter(first_name__icontains = word).values('id', 'first_name', 'last_name', 'location__name', 'location__customer__name', 'product__name')
                contacts_by_last_name  = ContactPerson.objects.filter(last_name__icontains  = word).values('id', 'first_name', 'last_name', 'location__name', 'location__customer__name', 'product__name')
                contacts               = list(chain(contacts_by_first_name, contacts_by_last_name))
        else:
            if len(words) == 2:
                contacts_one = ContactPerson.objects.filter(first_name__iexact = words[0], last_name__iexact = words[1]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts_two = ContactPerson.objects.filter(first_name__iexact = words[1], last_name__iexact = words[0]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts     = list(chain(contacts_one, contacts_two))
            elif len(words) == 3:
                contacts_one = ContactPerson.objects.filter(first_name__iexact = words[0] + words[1], last_name__iexact = words[2]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts_two = ContactPerson.objects.filter(first_name__iexact = words[1] + words[2], last_name__iexact = words[0]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts     = list(chain(contacts_one, contacts_two))
            else:
                contacts_by_first_name = ContactPerson.objects.filter(first_name__iexact = word).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts_by_last_name  = ContactPerson.objects.filter(last_name__iexact  = word).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts               = list(chain(contacts_by_first_name, contacts_by_last_name))

        for contact in contacts:
            if not contact['product__name']:
                contact['product__name'] = 'Nicht zugewiesen'

        return list(contacts)
