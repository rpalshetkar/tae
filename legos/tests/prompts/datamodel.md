You are best python programmer who followes stricted possible coding standards

My Input is YAML file which has data model related parameters the spec as in below
My YAML consists of

-   model as a name
-   keys as list of fields which is optional primary key to ensure uniqueness
-   id field is string concatenation of the keys fields
-   Enumeration kind of field
    -   Special would have hardcode list of keys and values(to be avoided) or datasource, key, value returned
    -   Eg person id could be xPeople repo where Alias|Personal ID|Email is shown as value and Personal ID is stored as key
    -   It may need to have access to another field in the model which is used as key to filter on the datasource to find relevant records.
    -   It could also be just simple key, value pair where if value is not given key would be used instead to show in picklist
-   Field within the model could have references as a field which can take datasource, key, value, query. Value is used when UI is rendered as select/multiselect
-   Model would support int, float, str, list, dict, enumeration, nested model field which can take another model or same model
-   Each field has data type, we will stick to native data types as available in typing library
-   The list field could be comma separated list which then gets split into array if required when passed from URL api
-   You know how to best infer python datatype to equivalent UI components including select or multiselect, booleans as checkbox etc.
-   Ideally for each python type you should have all UI related parametrs
-   For example, if int then min max or say if str then it is text where min and max length or if required or range or say email
-   Field would also have a way to specify order in which it would get rendered
-   Model would enforce compliance to the schema when reading/saving as well as rendering

My output should be sample yaml across give datatype and fields. You may need two yaml files to simulate nested model.

Your job is to

-   WRITE python program to generate ATTR based model boilerplate
-   WRITE python program to generate Schema definitions yaml boilerpate which serves UI as well Flask/FastAPI UI for CRUD
-   Field Class should be written to support above behaviours and used in Model class and all implementations should derive from Model abstractions
-   Write test case to test this foundational build where you have two yaml files which is driver for this. Two yamls to simulate nesting

UI Spec

For each int, float, datetime, date, text, note, list, multiselect, select, switch/boolean, email
what kind of UI component to be used and what are the paramters to the UI.
Put them in YAML file. Pls include all datatypes
