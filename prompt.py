

doc_generation_instruction = (
    "You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. "
    "The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.\n\n"
    "Currently, you are in a project and the related hierarchical structure of this project is as follows\n"
    "{project_structure}\n\n"
    "The path of the document you need to generate in this project is {file_path}.\n"
    'Now you need to generate a document for a {code_type_tell}, whose name is `{code_name}`.\n\n'
    "The content of the code is as follows:\n"
    "```C++\n"
    "{code_content}\n\n"
    "```\n\n"
    "{reference_letter}\n"
    "{referencer_content}\n\n"
    "Please generate a detailed explanation document for this object based on the code of the target object itself {combine_ref_situation}.\n\n"
    "Please write out the function of this {code_type_tell} in bold plain text, followed by a detailed analysis in plain text "
    "(including all details), in language {language} to serve as the documentation for this part of the code.\n\n"
    "The standard format is as follows:\n\n"
    "> ### {code_name}\n"
    "> The function of {code_name} is XXX. (Only code name and one sentence function description are required)\n>\n"
    "{parameters_note}"
    "> **Code Description**: The description of this {code_type_tell}."
    "(Detailed and CERTAIN code analysis and description...{has_relationship})\n>\n"
    "> **Note**: Points to note about the use of the code\n>\n"
    "{have_return_tell}"
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
The directory structure provided by the user is wrapped with [] 
and the parent-child relationship between directories is indicated by a 2-space indentation, 
for example: the user gives the following project structure 
[
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
].
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
