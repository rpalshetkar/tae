**Prompt:**

You are best python programmer who followes stricted possible coding standards

My Input is YAML file which has data model related parameters. 


My YAML consists of 
- model as a name
- keys as list of fields which is optional primary key to ensure uniqueness
- id field is string concatenation of the keys fields
- enumeration field type which is special would have hardcode list of keys and values(to be avoided) or datasource, key, value returned
- enumeration for person id could be xPeople repo where Alias|Personal ID|Email is shown as value and Personal ID is stored as key
- enumeration could also refer to query field.
- enumeration also could be just simple key, value pair where if value is not given key would be used instead to show in picklist
- model would also have foreign key which has three fields, datasource, key, value. Value is used when UI is rendered as select/multiselect
- model would support int, float, str, list, dict, enumeration, nested model field which can take another model or same model
- Each field has data type, we will stick to native data types as available in typing library
- The list field could be comma separated list which then gets split into array if required when passed from URL api
- You know how to best infer python datatype to equivalent UI components including select or multiselect, booleans as checkbox etc. 
- Ideally for each python type you should have all UI related parametrs 
- For example, if int then min max or say if str then it is text where min and max length or if required or range or say email
- field would also have a way to specify order in which it would get rendered
- Model would enforce compliance to the schema when reading/saving as well as rendering

My output should be sample yaml across give datatype and fields You may need two yaml files to simulate nested model. 
As an example use country population and nested field as state populations using public api which can give this information. 
Here say enumeration for state needs to be smart to know that I need to pick up states for the country which I have focus on

Your job is to 
1. Give me two yaml files which is driver
2. WRITE python program to generate ATTR based model boilerplate for these two yamls
3. WRITE python program to generate Schema definitions yaml which is refered by UI as well as CRUD flask API. So has UI elements also
4. Create Stereamlit app which show the table of rows for Clients and their orders.


then python code to generate ATTR based model file and full model specification

which based on model schema metadata and field types can drive any
of the UI frameworks like ReactJS, Streamlit or Dash. 

The data model here also is the data exchange format for API which would be delivered via
Flask or FastAPI. 

You generate code for schema definition for UI as well as CRUD API as well as Data Model using ATTRS library

The YAM
```yaml
models:
  User:
    attributes:
      username:
        type: string
        ui_element: text
        validator: required
        ui:
          length: 50
          order: 1
      age:
        type: integer
        ui_element: number
        validator: range(0, 120)
        ui:
          order: 2
      email:
        type: string
        ui_element: text
        validator: email
        ui:
          length: 100
          order: 3
      preferences:
        type: list
        ui_element: multiselect
        ui:
          order: 4
      is_active:
        type: boolean
        ui_element: checkbox
        ui:
          order: 5
      data:
        type: dict
        ui_element: textarea
        ui:
          length: 500
          order: 6
```

The function should read the YAML file, create the attrs models, and return a dictionary of the generated models, where the keys are the model names and the values are the corresponding model classes. Additionally, the function should handle merging UI properties from the data type definitions and the individual attribute definitions.

---

This prompt encapsulates all your requests and provides a clear direction for implementing the desired functionality. If you have any further modifications or additional features you'd like to include, feel free to let me know!
