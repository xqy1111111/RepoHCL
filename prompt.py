import json

doc_generation_instruction = (
    "You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. "
    "The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.\n\n"
    "Currently, you are in a project and the related hierarchical structure of this project is as follows\n"
    "{project_structure}\n\n"
    "The path of the document you need to generate in this project is {file_path}.\n"
    'Now you need to generate a document for a {code_type_tell}, whose name is `{code_name}`.\n\n'
    "{code_content}\n\n"
    "{reference_letter}\n"
    "{referencer_content}\n\n"
    "Please generate a detailed explanation document for this object based on the code of the target object itself and combine it with its calling situation in the project.\n\n"
    "Please write out the function of this {code_type_tell} in bold plain text, followed by a detailed analysis in plain text "
    "(including all details), in language {language} to serve as the documentation for this part of the code.\n\n"
    "The standard format is as follows:\n\n"
    # "> ### {code_name}\n"
    "> The function of {code_name} is XXX. (Only code name and one sentence function description are required)\n>\n"
    "{parameters_note}"
    "> **Code Details**\n"
    "The description of this {code_type_tell}. (Detailed and CERTAIN code analysis and description...{has_relationship})\n"
    ">\n"
    "> **Example**\n"
    "{example}"
    "> \n\n"
    "Please note:\n"
    "- Any part of the content you generate SHOULD NOT CONTAIN Markdown hierarchical heading and divider syntax.\n"
    "- Write mainly in the desired language. If necessary, you can write with some English words in the analysis and description "
    "to enhance the document's readability because you do not need to translate the function name or variable name into the target language.\n"
)

documentation_guideline = (
    "Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know "
    "you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation "
    "for the target object in {language} in a professional way."
)

structure_trimmer = '''
You are a professional code base organization assistant. 
Your task is to help users clean up the directory structure of the C/C++ project repository and remove paths that are not related to business code.
You need to understand the common folders and files of C/C++ projects, 
and be able to identify which are the business code files to implement core functions 
and which are non-business code files such as codes for documents and tests. 
According to the project structure provided by the user, you retain the necessary paths and return. 
Please keep the input and output formats consistent and return the modified results directly without explaining the reasons.
The directory structure provided by the user is indicated by a 2-space indentation, 
for example: the user gives the following project structure

my_cpp_project
  doc 
    doc.cpp        
  include
    my_cpp_project
      my_class.h
  src
    main.cpp
    my_class.cpp
    test_main.cpp
  test
    test_main.cpp
    test_my_class.cpp
    
You should think like this:
(1) The .c files under doc and test seem to be used for documentation and testing, not business code, so they should be excluded. 
(2) Although test_main.cpp is in the src directory, it is also used for testing based on its name, so it should be excluded.
And output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp
'''

modules_summarize_prompt = '''
You are an expert in software architecture analysis. Your task is to review function descriptions from a C++ code repository and organize them into multiple functional modules based on their purpose and interrelations. You will employ a structured approach to ensure accurate and insightful categorization.
For each identified functional module, you should output a structured summary in language {language} using the following format:

> ### (Module Name)
> (A concise paragraph summarizing the module's purpose, how it contributes to solving specific problems, and which functions work together within the module.)
> **Functions List** (A list of function names included in this module)
> - Function1
> - Function2

You'd better consider the following workflow:
1. Identify Core Functionality. Start by reading through all function descriptions to get a broad understanding of the available functionalities and think about the core tasks or operations that these functions enable.
2. Define Functional Modules. Based on the core functionalities, define initial functional modules that encapsulate related tasks or operations. Use your expertise to determine logical groupings of functions that contribute to similar outcomes or processes.
3. Analyze Function Interdependencies. Examine how functions interact with one another. Consider whether they are called in sequence, share data, or serve complementary purposes. Recognize that a single function can be part of multiple modules if it serves different roles or contexts.
4. Refine Module Definitions. Review and adjust the boundaries of the modules as needed to ensure they accurately reflect the relationships between functions. Ensure that each module's summary clearly articulates its unique value and contribution to the overall system.
5. Generate Documentation. Write a summary for each module using the provided format you finally decide and put them together. Don't include any other content in the output. 

Please Note:
- Write mainly in the desired language. If necessary, you can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
- Use the full function name with the return type and parameters, not the abbreviation.
- Try to put every function into at least one module unless the function is really useless.

Now a list of function descriptions are provided as follows, you can start working.
{function_list}
'''

modules_enhance_prompt = '''
You are an AI code assistant. Your task is to refer to the function documentation of a C++ module and make up a use case that combines multiple functions from the module to solve a specific problem or achieve a particular outcome. The use case should be realistic and demonstrate the functionality of the module.'
You should output using the following format with comments in {language}:

> ```C++
> (use case)
> ```

You'd better consider the following workflow:
1. Understand the Module. Read through the function descriptions and the module summary to gain a comprehensive understanding of the module's purpose and functionality. Identify the key functions that contribute to the module's core operations.
2. Define the Use Case. Based on the functions available in the module, define a specific problem or scenario that the module can address. Consider how multiple functions can work together to achieve a desired outcome or solve a particular issue.
3. Develop the Use Case. You can write some comments in the codes helping reader understand the scenario.

Please Note:
- Write mainly in the desired language. If necessary, you can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
- Only output the use case. Never include any other content.  

Here is the documentation of the module you need to enhance:
{module_doc}
'''