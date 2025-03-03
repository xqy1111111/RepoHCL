
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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is resource/md5/md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`.

The code of the Method is as follows:

```C++
void MD5Decode(unsigned int *output,unsigned char *input,unsigned int len) {
	unsigned int i = 0,j = 0;
	while(j < len) {
		output[i] = (input[j]) | (input[j+1] << 8) | (input[j+2] << 16) | (input[j+3] << 24);
		i++;
		j+=4;
	}
}
```




Please generate a detailed explanation document for this object based on the code of the target object itself and combine it with its calling situation in the project.

Please write out the function of this Method in bold plain text, followed by a detailed analysis in plain text (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> ... (Briefly describe the Method in one sentence like `The method is to xxx`)
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> ... (Detailed and CERTAIN code analysis of the Method. )
> #### Example
> ```C++
> ... (mock possible usage examples of the Method with codes. )

> ```
Please note:
- The headers in the format like `#### xxx` are fixed, never change or translate them.
- Never add new headers.

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is resource/md5/md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`.

The code of the Method is as follows:

```C++
void MD5Decode(unsigned int *output,unsigned char *input,unsigned int len) {
	unsigned int i = 0,j = 0;
	while(j < len) {
		output[i] = (input[j]) | (input[j+1] << 8) | (input[j+2] << 16) | (input[j+3] << 24);
		i++;
		j+=4;
	}
}
```




Please generate a detailed explanation document for this object based on the code of the target object itself and combine it with its calling situation in the project.

Please write out the function of this Method in bold plain text, followed by a detailed analysis in plain text (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> (Briefly describe the Method in one sentence)
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> (Detailed and CERTAIN code analysis of the Method. )
> #### Example
> ```C++
> (Mock possible usage examples of the Method with codes. )
> ```

Please note:
- The headers in the format like `#### xxx` are fixed, never change or translate them.
- Never add new headers.

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is resource/md5/md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`.

The code of the Method is as follows:

```C++
void MD5Decode(unsigned int *output,unsigned char *input,unsigned int len) {
	unsigned int i = 0,j = 0;
	while(j < len) {
		output[i] = (input[j]) | (input[j+1] << 8) | (input[j+2] << 16) | (input[j+3] << 24);
		i++;
		j+=4;
	}
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> (Briefly describe the Method in one sentence)
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> (Detailed and CERTAIN code analysis of the Method. )
> #### Example
> ```C++
> (Mock possible usage examples of the Method with codes. )
> ```

Please note:
- The headers in the format like `#### xxx` are fixed, don't change or translate them.
- Never add new headers.

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is resource/md5/md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Transform(unsigned int [4] state, unsigned char [64] block)`.

The code of the Method is as follows:

```C++
void MD5Transform(unsigned int state[4],unsigned char block[64]) {
	unsigned int a = state[0];
	unsigned int b = state[1];
	unsigned int c = state[2];
	unsigned int d = state[3];
	unsigned int x[64];

	MD5Decode(x,block,64);

	FF(a, b, c, d, x[ 0], 7, 0xd76aa478);
	FF(d, a, b, c, x[ 1], 12, 0xe8c7b756);
	FF(c, d, a, b, x[ 2], 17, 0x242070db);
	FF(b, c, d, a, x[ 3], 22, 0xc1bdceee);
	FF(a, b, c, d, x[ 4], 7, 0xf57c0faf);
	FF(d, a, b, c, x[ 5], 12, 0x4787c62a);
	FF(c, d, a, b, x[ 6], 17, 0xa8304613);
	FF(b, c, d, a, x[ 7], 22, 0xfd469501);
	FF(a, b, c, d, x[ 8], 7, 0x698098d8);
	FF(d, a, b, c, x[ 9], 12, 0x8b44f7af);
	FF(c, d, a, b, x[10], 17, 0xffff5bb1);
	FF(b, c, d, a, x[11], 22, 0x895cd7be);
	FF(a, b, c, d, x[12], 7, 0x6b901122);
	FF(d, a, b, c, x[13], 12, 0xfd987193);
	FF(c, d, a, b, x[14], 17, 0xa679438e);
	FF(b, c, d, a, x[15], 22, 0x49b40821);

	GG(a, b, c, d, x[ 1], 5, 0xf61e2562);
	GG(d, a, b, c, x[ 6], 9, 0xc040b340);
	GG(c, d, a, b, x[11], 14, 0x265e5a51);
	GG(b, c, d, a, x[ 0], 20, 0xe9b6c7aa);
	GG(a, b, c, d, x[ 5], 5, 0xd62f105d);
	GG(d, a, b, c, x[10], 9,  0x2441453);
	GG(c, d, a, b, x[15], 14, 0xd8a1e681);
	GG(b, c, d, a, x[ 4], 20, 0xe7d3fbc8);
	GG(a, b, c, d, x[ 9], 5, 0x21e1cde6);
	GG(d, a, b, c, x[14], 9, 0xc33707d6);
	GG(c, d, a, b, x[ 3], 14, 0xf4d50d87);
	GG(b, c, d, a, x[ 8], 20, 0x455a14ed);
	GG(a, b, c, d, x[13], 5, 0xa9e3e905);
	GG(d, a, b, c, x[ 2], 9, 0xfcefa3f8);
	GG(c, d, a, b, x[ 7], 14, 0x676f02d9);
	GG(b, c, d, a, x[12], 20, 0x8d2a4c8a);


	HH(a, b, c, d, x[ 5], 4, 0xfffa3942);
	HH(d, a, b, c, x[ 8], 11, 0x8771f681);
	HH(c, d, a, b, x[11], 16, 0x6d9d6122);
	HH(b, c, d, a, x[14], 23, 0xfde5380c);
	HH(a, b, c, d, x[ 1], 4, 0xa4beea44);
	HH(d, a, b, c, x[ 4], 11, 0x4bdecfa9);
	HH(c, d, a, b, x[ 7], 16, 0xf6bb4b60);
	HH(b, c, d, a, x[10], 23, 0xbebfbc70);
	HH(a, b, c, d, x[13], 4, 0x289b7ec6);
	HH(d, a, b, c, x[ 0], 11, 0xeaa127fa);
	HH(c, d, a, b, x[ 3], 16, 0xd4ef3085);
	HH(b, c, d, a, x[ 6], 23,  0x4881d05);
	HH(a, b, c, d, x[ 9], 4, 0xd9d4d039);
	HH(d, a, b, c, x[12], 11, 0xe6db99e5);
	HH(c, d, a, b, x[15], 16, 0x1fa27cf8);
	HH(b, c, d, a, x[ 2], 23, 0xc4ac5665);


	II(a, b, c, d, x[ 0], 6, 0xf4292244);
	II(d, a, b, c, x[ 7], 10, 0x432aff97);
	II(c, d, a, b, x[14], 15, 0xab9423a7);
	II(b, c, d, a, x[ 5], 21, 0xfc93a039);
	II(a, b, c, d, x[12], 6, 0x655b59c3);
	II(d, a, b, c, x[ 3], 10, 0x8f0ccc92);
	II(c, d, a, b, x[10], 15, 0xffeff47d);
	II(b, c, d, a, x[ 1], 21, 0x85845dd1);
	II(a, b, c, d, x[ 8], 6, 0x6fa87e4f);
	II(d, a, b, c, x[15], 10, 0xfe2ce6e0);
	II(c, d, a, b, x[ 6], 15, 0xa3014314);
	II(b, c, d, a, x[13], 21, 0x4e0811a1);
	II(a, b, c, d, x[ 4], 6, 0xf7537e82);
	II(d, a, b, c, x[11], 10, 0xbd3af235);
	II(c, d, a, b, x[ 2], 15, 0x2ad7d2bb);
	II(b, c, d, a, x[ 9], 21, 0xeb86d391);
	state[0] += a;
	state[1] += b;
	state[2] += c;
	state[3] += d;
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`

**Document**:

> ### void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)
> (Briefly describe the Method in one sentence)
> 
> #### Parameters
> - output: 指向一个无符号整数数组的指针，用于存储解码后的结果。
> - input: 指向一个无符号字符数组的指针，包含待解码的输入数据。
> - len: 输入数据的长度（以字节为单位）。
> 
> #### Code Details
> (Detailed and CERTAIN code analysis of the Method. )
> 
> `MD5Decode` 方法的主要功能是将输入的字节数组 `input` 解码为无符号整数数组 `output`。该方法假设输入数据是以4字节为一组进行编码的，每组4字节对应一个32位的无符号整数。具体来说：
> 
> 1. 初始化两个索引变量 `i` 和 `j` 为0，分别用于遍历 `output` 和 `input` 数组。
> 2. 使用 `while` 循环遍历输入数据，直到处理完所有指定长度的数据。
> 3. 在每次循环中，从 `input` 中读取4个连续的字节，并将它们组合成一个32位的无符号整数：
>    - `input[j]` 是最低有效字节 (Least Significant Byte, LSB)。
>    - `input[j+1] << 8` 将第二个字节左移8位。
>    - `input[j+2] << 16` 将第三个字节左移16位。
>    - `input[j+3] << 24` 将第四个字节左移24位。
> 4. 使用按位或运算符 `|` 将这四个字节组合成一个32位的无符号整数，并将其存储在 `output[i]` 中。
> 5. 更新索引变量 `i` 和 `j`，以便处理下一组4字节的数据。
> 
> 需要注意的是，该方法假设输入数据的长度 `len` 是4的倍数。如果 `len` 不是4的倍数，则可能会导致未定义行为。
> 
> #### Example
> ```C++
> #include <stdio.h>
> 
> void MD5Decode(unsigned int *output, unsigned char *input, unsigned int len);
> 
> int main() {
>     unsigned char input[] = {0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0};
>     unsigned int output[2];
>     unsigned int len = sizeof(input);
> 
>     MD5Decode(output, input, len);
> 
>     printf("Decoded values:\n");
>     for (int i = 0; i < 2; ++i) {
>         printf("output[%d] = 0x%X\n", i, output[i]);
>     }
> 
>     return 0;
> }
> ```
> 
> 在这个例子中，`input` 数组包含8个字节的数据，`MD5Decode` 方法将其解码为两个32位的无符号整数并存储在 `output` 数组中。输出结果将显示解码后的值。
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> (Briefly describe the Method in one sentence)
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> (Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective)
> #### Example
> ```C++
> (Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.)
> ```

Please note:
- The headers in the format like `#### xxx` are fixed, don't change or translate them.
- Never add new headers.

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is resource/md5/md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`.

The code of the Method is as follows:

```C++
void MD5Decode(unsigned int *output,unsigned char *input,unsigned int len) {
	unsigned int i = 0,j = 0;
	while(j < len) {
		output[i] = (input[j]) | (input[j+1] << 8) | (input[j+2] << 16) | (input[j+3] << 24);
		i++;
		j+=4;
	}
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. 
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is resource/md5/md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Transform(unsigned int [4] state, unsigned char [64] block)`.

The code of the Method is as follows:

```C++
void MD5Transform(unsigned int state[4],unsigned char block[64]) {
	unsigned int a = state[0];
	unsigned int b = state[1];
	unsigned int c = state[2];
	unsigned int d = state[3];
	unsigned int x[64];

	MD5Decode(x,block,64);

	FF(a, b, c, d, x[ 0], 7, 0xd76aa478);
	FF(d, a, b, c, x[ 1], 12, 0xe8c7b756);
	FF(c, d, a, b, x[ 2], 17, 0x242070db);
	FF(b, c, d, a, x[ 3], 22, 0xc1bdceee);
	FF(a, b, c, d, x[ 4], 7, 0xf57c0faf);
	FF(d, a, b, c, x[ 5], 12, 0x4787c62a);
	FF(c, d, a, b, x[ 6], 17, 0xa8304613);
	FF(b, c, d, a, x[ 7], 22, 0xfd469501);
	FF(a, b, c, d, x[ 8], 7, 0x698098d8);
	FF(d, a, b, c, x[ 9], 12, 0x8b44f7af);
	FF(c, d, a, b, x[10], 17, 0xffff5bb1);
	FF(b, c, d, a, x[11], 22, 0x895cd7be);
	FF(a, b, c, d, x[12], 7, 0x6b901122);
	FF(d, a, b, c, x[13], 12, 0xfd987193);
	FF(c, d, a, b, x[14], 17, 0xa679438e);
	FF(b, c, d, a, x[15], 22, 0x49b40821);

	GG(a, b, c, d, x[ 1], 5, 0xf61e2562);
	GG(d, a, b, c, x[ 6], 9, 0xc040b340);
	GG(c, d, a, b, x[11], 14, 0x265e5a51);
	GG(b, c, d, a, x[ 0], 20, 0xe9b6c7aa);
	GG(a, b, c, d, x[ 5], 5, 0xd62f105d);
	GG(d, a, b, c, x[10], 9,  0x2441453);
	GG(c, d, a, b, x[15], 14, 0xd8a1e681);
	GG(b, c, d, a, x[ 4], 20, 0xe7d3fbc8);
	GG(a, b, c, d, x[ 9], 5, 0x21e1cde6);
	GG(d, a, b, c, x[14], 9, 0xc33707d6);
	GG(c, d, a, b, x[ 3], 14, 0xf4d50d87);
	GG(b, c, d, a, x[ 8], 20, 0x455a14ed);
	GG(a, b, c, d, x[13], 5, 0xa9e3e905);
	GG(d, a, b, c, x[ 2], 9, 0xfcefa3f8);
	GG(c, d, a, b, x[ 7], 14, 0x676f02d9);
	GG(b, c, d, a, x[12], 20, 0x8d2a4c8a);


	HH(a, b, c, d, x[ 5], 4, 0xfffa3942);
	HH(d, a, b, c, x[ 8], 11, 0x8771f681);
	HH(c, d, a, b, x[11], 16, 0x6d9d6122);
	HH(b, c, d, a, x[14], 23, 0xfde5380c);
	HH(a, b, c, d, x[ 1], 4, 0xa4beea44);
	HH(d, a, b, c, x[ 4], 11, 0x4bdecfa9);
	HH(c, d, a, b, x[ 7], 16, 0xf6bb4b60);
	HH(b, c, d, a, x[10], 23, 0xbebfbc70);
	HH(a, b, c, d, x[13], 4, 0x289b7ec6);
	HH(d, a, b, c, x[ 0], 11, 0xeaa127fa);
	HH(c, d, a, b, x[ 3], 16, 0xd4ef3085);
	HH(b, c, d, a, x[ 6], 23,  0x4881d05);
	HH(a, b, c, d, x[ 9], 4, 0xd9d4d039);
	HH(d, a, b, c, x[12], 11, 0xe6db99e5);
	HH(c, d, a, b, x[15], 16, 0x1fa27cf8);
	HH(b, c, d, a, x[ 2], 23, 0xc4ac5665);


	II(a, b, c, d, x[ 0], 6, 0xf4292244);
	II(d, a, b, c, x[ 7], 10, 0x432aff97);
	II(c, d, a, b, x[14], 15, 0xab9423a7);
	II(b, c, d, a, x[ 5], 21, 0xfc93a039);
	II(a, b, c, d, x[12], 6, 0x655b59c3);
	II(d, a, b, c, x[ 3], 10, 0x8f0ccc92);
	II(c, d, a, b, x[10], 15, 0xffeff47d);
	II(b, c, d, a, x[ 1], 21, 0x85845dd1);
	II(a, b, c, d, x[ 8], 6, 0x6fa87e4f);
	II(d, a, b, c, x[15], 10, 0xfe2ce6e0);
	II(c, d, a, b, x[ 6], 15, 0xa3014314);
	II(b, c, d, a, x[13], 21, 0x4e0811a1);
	II(a, b, c, d, x[ 4], 6, 0xf7537e82);
	II(d, a, b, c, x[11], 10, 0xbd3af235);
	II(c, d, a, b, x[ 2], 15, 0x2ad7d2bb);
	II(b, c, d, a, x[ 9], 21, 0xeb86d391);
	state[0] += a;
	state[1] += b;
	state[2] += c;
	state[3] += d;
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`

**Document**:

> ### void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)
> 将输入的字节数组解码为无符号整数数组。
> 
> #### Parameters
> - `output`: 一个指向无符号整数数组的指针，用于存储解码后的结果。
> - `input`: 一个指向字节数组的指针，包含待解码的数据。
> - `len`: 输入字节数组的长度（以字节为单位）。
> 
> #### Code Details
> 该方法的主要功能是将输入的字节数组 `input` 解码为无符号整数数组 `output`。具体来说，它每次从 `input` 中读取4个字节，并将这4个字节组合成一个32位的无符号整数，然后将其存储到 `output` 数组中。这个过程通过以下步骤实现：
> 
> 1. 初始化两个索引变量 `i` 和 `j`，分别用于遍历 `output` 和 `input` 数组。
> 2. 使用 `while` 循环遍历 `input` 数组，直到处理完所有指定长度的字节。
> 3. 在每次循环中，从 `input[j]` 开始读取4个连续的字节，并通过按位或运算和移位操作将它们组合成一个32位的无符号整数：
>    - `input[j]` 是最低有效字节 (Least Significant Byte, LSB)。
>    - `input[j+1] << 8` 将第二个字节左移8位。
>    - `input[j+2] << 16` 将第三个字节左移16位。
>    - `input[j+3] << 24` 将第四个字节左移24位。
> 4. 将组合后的32位无符号整数存储到 `output[i]` 中。
> 5. 更新索引变量 `i` 和 `j`，以便在下一次循环中处理下一个4字节块。
> 
> 需要注意的是，`len` 必须是4的倍数，否则可能会导致未定义行为或访问越界错误。
> 
> #### Example
> ```C++
> #include <stdio.h>
> 
> void MD5Decode(unsigned int *output, unsigned char *input, unsigned int len);
> 
> int main() {
>     unsigned char input[] = {0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0};
>     unsigned int output[2];
>     unsigned int len = sizeof(input);
> 
>     MD5Decode(output, input, len);
> 
>     printf("Decoded values:\n");
>     for (int i = 0; i < 2; ++i) {
>         printf("output[%d] = 0x%X\n", i, output[i]);
>     }
> 
>     return 0;
> }
> ```
> 
> 在这个例子中，`input` 数组包含8个字节的数据，`MD5Decode` 方法会将这些字节解码为两个32位的无符号整数并存储在 `output` 数组中。输出结果将是：
> ```
> Decoded values:
> output[0] = 0x78563412
> output[1] = 0xF0DEBC9A
> ```
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is resource/md5/md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)`.

The code of the Method is as follows:

```C++
void MD5Update(MD5_CTX *context,unsigned char *input,unsigned int inputlen)
{
	unsigned int i = 0,index = 0,partlen = 0;
	index = (context->count[0] >> 3) & 0x3F;
	partlen = 64 - index;
	context->count[0] += inputlen << 3;
	if(context->count[0] < (inputlen << 3)) {
		context->count[1]++;
	}
	context->count[1] += inputlen >> 29;

	if(inputlen >= partlen) {
		memcpy(&context->buffer[index],input,partlen);
		MD5Transform(context->state,context->buffer);
		for(i = partlen;i+64 <= inputlen;i+=64) {
			MD5Transform(context->state,&input[i]);
		}
		index = 0;
	} else {
		i = 0;
	}
	
	memcpy(&context->buffer[index],&input[i],inputlen-i);
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Transform(unsigned int [4] state, unsigned char [64] block)`

**Document**:

> ### void MD5Transform(unsigned int [4] state, unsigned char [64] block)
> 对给定的64字节块进行MD5变换，并更新状态值。
> 
> #### Parameters
> - `state`: 一个包含4个无符号整数的数组，表示当前的MD5状态。该方法会根据输入块更新这些状态值。
> - `block`: 一个包含64个字节的数组，表示要处理的数据块。
> 
> #### Code Details
> `MD5Transform` 方法的主要功能是对给定的64字节数据块进行MD5变换，并更新传入的状态值。具体步骤如下：
> 
> 1. **初始化状态变量**：
>    - 将传入的 `state` 数组中的四个元素分别赋值给局部变量 `a`, `b`, `c`, `d`。这四个变量将用于后续的计算。
> 
> 2. **解码输入块**：
>    - 调用 `MD5Decode` 方法将输入的64字节数组 `block` 解码为一个包含16个无符号整数的数组 `x`。每个无符号整数由4个连续的字节组成。
> 
> 3. **执行四轮变换**：
>    - MD5算法包括四轮不同的变换，每轮包含16次操作。每一轮使用不同的函数（FF, GG, HH, II）和常量来更新状态变量 `a`, `b`, `c`, `d`。
>    - 每次操作都会根据特定的索引从 `x` 数组中选择一个元素，并结合一个旋转位移量和一个常量值来更新状态变量。
> 
> 4. **更新状态**：
>    - 在所有变换完成后，将更新后的状态变量 `a`, `b`, `c`, `d` 分别加回到传入的 `state` 数组中，从而完成状态的更新。
> 
> 此方法是MD5哈希算法的核心部分，它通过一系列复杂的数学运算确保了输入数据的唯一性和不可逆性。`MD5Transform` 方法通常在处理完每64字节的数据块后被调用，以逐步构建最终的哈希值。
> 
> #### Example
> ```C++
> #include <stdio.h>
> #include "md5.h"
> 
> int main() {
>     unsigned int state[4] = {0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476};
>     unsigned char block[64] = {
>         // 填充64个字节的数据
>         0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38,
>         0x39, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36,
>         0x37, 0x38, 0x39, 0x30, 0x31, 0x32, 0x33, 0x34,
>         0x35, 0x36, 0x37, 0x38, 0x39, 0x30, 0x31, 0x32,
>         0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30,
>         0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38,
>         0x39, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36,
>         0x37, 0x38, 0x39, 0x30, 0x31, 0x32, 0x33, 0x34
>     };
> 
>     MD5Transform(state, block);
> 
>     printf("Updated state values:\n");
>     for (int i = 0; i < 4; ++i) {
>         printf("state[%d] = 0x%X\n", i, state[i]);
>     }
> 
>     return 0;
> }
> ```
> 
> 在这个例子中，`state` 数组初始化为MD5算法的标准初始值，`block` 数组填充了64个字节的数据。调用 `MD5Transform` 方法后，`state` 数组中的值会被更新，以反映对输入数据块的MD5变换结果。
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is resource/md5/md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Encode(unsigned char * output, unsigned int * input, unsigned int len)`.

The code of the Method is as follows:

```C++
void MD5Encode(unsigned char *output,unsigned int *input,unsigned int len) {
	unsigned int i = 0,j = 0;
	while(j < len) {
		output[j] = input[i] & 0xFF;
		output[j+1] = (input[i] >> 8) & 0xFF;
		output[j+2] = (input[i] >> 16) & 0xFF;
		output[j+3] = (input[i] >> 24) & 0xFF;
		i++;
		j+=4;
	}
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. 
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is resource/md5/md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Final(MD5_CTX * context, unsigned char [16] digest)`.

The code of the Method is as follows:

```C++
void MD5Final(MD5_CTX *context,unsigned char digest[16]) {
	unsigned int index = 0,padlen = 0;
	unsigned char bits[8];
	index = (context->count[0] >> 3) & 0x3F;
	padlen = (index < 56)?(56-index):(120-index);
	MD5Encode(bits,context->count,8);
	MD5Update(context,PADDING,padlen);
	MD5Update(context,bits,8);
	MD5Encode(digest,context->state,16);
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Encode(unsigned char * output, unsigned int * input, unsigned int len)`

**Document**:

> ### void MD5Encode(unsigned char * output, unsigned int * input, unsigned int len)
> 将输入的整数数组编码为字节数组，使用MD5算法的标准字节序。
> 
> #### Parameters
> - `output`: 用于存储转换后的字节数组的指针。每个整数会被拆分为4个字节并依次存入此数组。
> - `input`: 包含待转换整数的数组指针。每个整数将被拆分为4个字节。
> - `len`: 输入数组中整数的数量。
> 
> #### Code Details
> 该函数的主要功能是将一个无符号整数数组（`unsigned int *input`）中的每个元素拆分为四个字节，并将这些字节按顺序写入到输出数组（`unsigned char *output`）中。具体步骤如下：
> 
> 1. 初始化两个索引变量 `i` 和 `j`，分别用于遍历 `input` 和 `output` 数组。
> 2. 使用 `while` 循环遍历 `input` 数组中的每个整数，直到处理完所有元素。
> 3. 对于每个整数：
>    - `output[j] = input[i] & 0xFF;`：提取整数的最低8位（即第一个字节），并将其存储在 `output[j]` 中。
>    - `output[j+1] = (input[i] >> 8) & 0xFF;`：将整数右移8位，提取第二个字节，并将其存储在 `output[j+1]` 中。
>    - `output[j+2] = (input[i] >> 16) & 0xFF;`：将整数右移16位，提取第三个字节，并将其存储在 `output[j+2]` 中。
>    - `output[j+3] = (input[i] >> 24) & 0xFF;`：将整数右移24位，提取第四个字节，并将其存储在 `output[j+3]` 中。
> 4. 每次处理完一个整数后，`i` 增加1，`j` 增加4，以便处理下一个整数和对应的四个字节。
> 
> #### Example
> ```C++
> #include <stdio.h>
> #include "md5.h"
> 
> int main() {
>     unsigned int input[] = {0x12345678, 0x9ABCDEF0};
>     unsigned char output[8];
>     MD5Encode(output, input, 2);
> 
>     for (int i = 0; i < 8; ++i) {
>         printf("%02X ", output[i]);
>     }
>     return 0;
> }
> ```
> 
> 上述示例代码将整数数组 `{0x12345678, 0x9ABCDEF0}` 转换为字节数组，并打印结果。输出应为：`78 56 34 12 F0 DE BC 9A`。
---
**Method**: `void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)`

**Document**:

> ### void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)
> 更新MD5上下文以包含新的输入数据。
> 
> #### Parameters
> - `context`: 指向 `MD5_CTX` 结构的指针，该结构包含当前的MD5状态和缓冲区。
> - `input`: 指向要处理的输入数据的指针，类型为 `unsigned char *`。
> - `inputlen`: 输入数据的长度，类型为 `unsigned int`。
> 
> #### Code Details
> `MD5Update` 方法的主要功能是将新的输入数据添加到现有的MD5上下文中，并根据需要调用 `MD5Transform` 来处理完整的64字节块。具体步骤如下：
> 
> 1. **计算当前缓冲区中的剩余空间**：
>    - 通过 `(context->count[0] >> 3) & 0x3F` 计算当前缓冲区中已使用的字节数 `index`，并确定剩余空间 `partlen = 64 - index`。
> 
> 2. **更新计数器**：
>    - 更新 `context->count` 数组以反映新输入数据的长度。`context->count[0]` 和 `context->count[1]` 分别表示低32位和高32位的位数计数。
>    - 如果输入数据长度超过 `partlen`，则需要处理多个64字节块。
> 
> 3. **处理输入数据**：
>    - 如果输入数据长度大于或等于 `partlen`，首先将剩余空间填满并调用 `MD5Transform` 处理第一个完整的64字节块。
>    - 然后，对于后续的每个64字节块，直接调用 `MD5Transform` 进行处理。
>    - 最后，将剩余的不足64字节的数据复制到缓冲区中。
> 
> 4. **处理小于一个完整块的输入数据**：
>    - 如果输入数据长度小于 `partlen`，则直接将其复制到缓冲区中。
> 
> 此方法确保了输入数据被正确地分块处理，并逐步构建最终的哈希值。`MD5Update` 方法通常在处理多段输入数据时被调用，例如在流式处理大文件或连续接收网络数据包时。
> 
> #### Example
> ```C++
> #include <stdio.h>
> #include "md5.h"
> 
> int main() {
>     MD5_CTX context;
>     unsigned char input[] = "The quick brown fox jumps over the lazy dog";
>     unsigned int inputlen = sizeof(input) - 1; // 不包括终止符
> 
>     MD5Init(&context);
>     MD5Update(&context, input, inputlen);
> 
>     unsigned char digest[16];
>     MD5Final(digest, &context);
> 
>     printf("MD5 Digest: ");
>     for (int i = 0; i < 16; ++i) {
>         printf("%02x", digest[i]);
>     }
>     printf("\n");
> 
>     return 0;
> }
> ```
> 
> 在这个例子中，`MD5_CTX` 结构初始化后，使用 `MD5Update` 方法将输入字符串添加到上下文中。最后，调用 `MD5Final` 方法完成哈希计算并输出结果。
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is resource/md5/md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Init(MD5_CTX * context)`.

The code of the Method is as follows:

```C++
void MD5Init(MD5_CTX *context) {
	context->count[0] = 0;
	context->count[1] = 0;
	context->state[0] = 0x67452301;
	context->state[1] = 0xEFCDAB89;
	context->state[2] = 0x98BADCFE;
	context->state[3] = 0x10325476;
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. 
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
- md5
  - main.c
  - md5.c
  - md5.h

The path of the document you need to generate in this project is resource/md5/main.c.
Now you need to generate a document for a Method, whose name is `int main(int argc, char *[] argv)`.

The code of the Method is as follows:

```C++
int main(int argc, char *argv[]) {
	int i, n;
	bool isfile = false;
	unsigned char decrypt[16];
	MD5_CTX md5;
	
	if(argc > 1 && strlen(argv[1]) == 2 && !memcmp(argv[1], "-f", 2)) {
		isfile = true;
	}
	
	if(argc == 1 || (argc == 2 && isfile)) {
		fprintf(stderr, "usage:\n    %s -f file ...\n    %s string ...\n", argv[0], argv[0]);
		return 1;
	}
	
	if(isfile) {
		FILE *fp;
		for(n=2; n<argc; n++) {
			fp = fopen(argv[n], "rb");
			if(fp == NULL) {
				fprintf(stderr, "File %s not exists, errno = %d, error = %s\n", argv[n], errno, strerror(errno));
				continue;
			}
			
			MD5Init(&md5);
			
			do {
				unsigned char encrypt[1024];
				while(!feof(fp)) {
					MD5Update(&md5, encrypt, fread(encrypt, 1, sizeof(encrypt), fp));
				}
				fclose(fp);
			} while(0);
			
			MD5Final(&md5, decrypt);

			for(i=0; i<16; i++) {
				printf("%02x", decrypt[i]);  //02x前需要加上 %
			}
			
			printf("  %s\n", argv[n]);
		}
	} else {
		for(n=1; n<argc; n++) {
			MD5Init(&md5);
			MD5Update(&md5, argv[n], strlen(argv[n]));
			MD5Final(&md5, decrypt);

			for(i=0; i<16; i++) {
				printf("%02x", decrypt[i]);  //02x前需要加上 %
			}
			
			printf("  %s\n", argv[n]);
		}
	}

	return 0;
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Init(MD5_CTX * context)`

**Document**:

> ### void MD5Init(MD5_CTX * context)
> 初始化 MD5 上下文结构体。
> 
> #### Parameters
> - context: 指向 MD5_CTX 结构体的指针，用于存储 MD5 算法的状态和计数信息。
> 
> #### Code Details
> `MD5Init` 函数用于初始化 MD5 上下文结构体 `MD5_CTX`。该函数将上下文中的计数器 `count` 和状态 `state` 初始化为特定的初始值，以确保后续的哈希计算能够正确进行。
> 
> 具体来说：
> - `context->count[0] = 0;` 和 `context->count[1] = 0;` 将两个64位计数器初始化为0。这两个计数器用于记录处理的消息长度。
> - `context->state[0] = 0x67452301;`、`context->state[1] = 0xEFCDAB89;`、`context->state[2] = 0x98BADCFE;` 和 `context->state[3] = 0x10325476;` 将状态数组 `state` 初始化为四个预定义的32位整数值。这些初始值是 MD5 算法标准中规定的，用于确保算法的一致性和正确性。
> 
> #### Example
> ```C++
> #include "md5.h"
> 
> int main() {
>     MD5_CTX context;
>     MD5Init(&context);
>     // 继续使用已初始化的 context 进行其他操作
>     return 0;
> }
> ```
> 
> 通过调用 `MD5Init` 函数，可以确保 `MD5_CTX` 结构体被正确初始化，从而为后续的哈希计算做好准备。
---
**Method**: `void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)`

**Document**:

> ### void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)
> 更新MD5上下文以包含新的输入数据。
> 
> #### Parameters
> - `context`: 指向 `MD5_CTX` 结构的指针，该结构包含当前的MD5状态和缓冲区。
> - `input`: 指向要处理的输入数据的指针，类型为 `unsigned char *`。
> - `inputlen`: 输入数据的长度，类型为 `unsigned int`。
> 
> #### Code Details
> `MD5Update` 方法的主要功能是将新的输入数据添加到现有的MD5上下文中，并根据需要调用 `MD5Transform` 来处理完整的64字节块。具体步骤如下：
> 
> 1. **计算当前缓冲区中的剩余空间**：
>    - 通过 `(context->count[0] >> 3) & 0x3F` 计算当前缓冲区中已使用的字节数 `index`，并确定剩余空间 `partlen = 64 - index`。
> 
> 2. **更新计数器**：
>    - 更新 `context->count` 数组以反映新输入数据的长度。`context->count[0]` 和 `context->count[1]` 分别表示低32位和高32位的位数计数。
>    - 如果输入数据长度超过 `partlen`，则需要处理多个64字节块。
> 
> 3. **处理输入数据**：
>    - 如果输入数据长度大于或等于 `partlen`，首先将剩余空间填满并调用 `MD5Transform` 处理第一个完整的64字节块。
>    - 然后，对于后续的每个64字节块，直接调用 `MD5Transform` 进行处理。
>    - 最后，将剩余的不足64字节的数据复制到缓冲区中。
> 
> 4. **处理小于一个完整块的输入数据**：
>    - 如果输入数据长度小于 `partlen`，则直接将其复制到缓冲区中。
> 
> 此方法确保了输入数据被正确地分块处理，并逐步构建最终的哈希值。`MD5Update` 方法通常在处理多段输入数据时被调用，例如在流式处理大文件或连续接收网络数据包时。
> 
> #### Example
> ```C++
> #include <stdio.h>
> #include "md5.h"
> 
> int main() {
>     MD5_CTX context;
>     unsigned char input[] = "The quick brown fox jumps over the lazy dog";
>     unsigned int inputlen = sizeof(input) - 1; // 不包括终止符
> 
>     MD5Init(&context);
>     MD5Update(&context, input, inputlen);
> 
>     unsigned char digest[16];
>     MD5Final(digest, &context);
> 
>     printf("MD5 Digest: ");
>     for (int i = 0; i < 16; ++i) {
>         printf("%02x", digest[i]);
>     }
>     printf("\n");
> 
>     return 0;
> }
> ```
> 
> 在这个例子中，`MD5_CTX` 结构初始化后，使用 `MD5Update` 方法将输入字符串添加到上下文中。最后，调用 `MD5Final` 方法完成哈希计算并输出结果。
---
**Method**: `void MD5Final(MD5_CTX * context, unsigned char [16] digest)`

**Document**:

> ### void MD5Final(MD5_CTX * context, unsigned char [16] digest)
> 完成MD5哈希计算并生成最终的16字节摘要。
> 
> #### Parameters
> - `context`: 指向 `MD5_CTX` 结构的指针，该结构包含当前的MD5状态和缓冲区。
> - `digest`: 用于存储最终16字节摘要的数组。每个元素是一个无符号字符（`unsigned char`），共16个元素。
> 
> #### Code Details
> `MD5Final` 方法的主要功能是完成MD5哈希计算，并将结果存储在 `digest` 数组中。具体步骤如下：
> 
> 1. **计算填充长度**：
>    - 计算当前缓冲区中已使用的字节数 `index`：`(context->count[0] >> 3) & 0x3F`。
>    - 根据 `index` 确定需要填充的字节数 `padlen`。如果 `index` 小于56，则填充到56；否则填充到120（即下一个64字节块的开始）。
> 
> 2. **编码位数计数器**：
>    - 使用 `MD5Encode(bits, context->count, 8)` 将 `context->count` 中的位数计数器编码为8字节的 `bits` 数组。这一步是为了确保在哈希计算中包含输入数据的总长度信息。
> 
> 3. **更新上下文**：
>    - 调用 `MD5Update(context, PADDING, padlen)` 将填充数据添加到上下文中。`PADDING` 是一个预定义的填充模式，通常以0x80开头，后面跟若干个0字节。
>    - 再次调用 `MD5Update(context, bits, 8)` 将位数计数器的编码结果添加到上下文中。
> 
> 4. **生成最终摘要**：
>    - 最后，调用 `MD5Encode(digest, context->state, 16)` 将 `context->state` 中的哈希状态编码为16字节的摘要，并存储在 `digest` 数组中。
> 
> 通过这些步骤，`MD5Final` 方法确保了所有输入数据被正确处理，并生成最终的MD5摘要。
> 
> #### Example
> ```C++
> #include <stdio.h>
> #include "md5.h"
> 
> int main() {
>     MD5_CTX context;
>     unsigned char input[] = "The quick brown fox jumps over the lazy dog";
>     unsigned int inputlen = sizeof(input) - 1; // 不包括终止符
> 
>     MD5Init(&context);
>     MD5Update(&context, input, inputlen);
> 
>     unsigned char digest[16];
>     MD5Final(digest, &context);
> 
>     printf("MD5 Digest: ");
>     for (int i = 0; i < 16; ++i) {
>         printf("%02x", digest[i]);
>     }
>     printf("\n");
> 
>     return 0;
> }
> ```
> 
> 在这个例子中，`MD5_CTX` 结构初始化后，使用 `MD5Update` 方法将输入字符串添加到上下文中。最后，调用 `MD5Final` 方法完成哈希计算并输出结果。
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`.

The code of the Method is as follows:

```C++
void MD5Decode(unsigned int *output,unsigned char *input,unsigned int len) {
	unsigned int i = 0,j = 0;
	while(j < len) {
		output[i] = (input[j]) | (input[j+1] << 8) | (input[j+2] << 16) | (input[j+3] << 24);
		i++;
		j+=4;
	}
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. 
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Transform(unsigned int [4] state, unsigned char [64] block)`.

The code of the Method is as follows:

```C++
void MD5Transform(unsigned int state[4],unsigned char block[64]) {
	unsigned int a = state[0];
	unsigned int b = state[1];
	unsigned int c = state[2];
	unsigned int d = state[3];
	unsigned int x[64];

	MD5Decode(x,block,64);

	FF(a, b, c, d, x[ 0], 7, 0xd76aa478);
	FF(d, a, b, c, x[ 1], 12, 0xe8c7b756);
	FF(c, d, a, b, x[ 2], 17, 0x242070db);
	FF(b, c, d, a, x[ 3], 22, 0xc1bdceee);
	FF(a, b, c, d, x[ 4], 7, 0xf57c0faf);
	FF(d, a, b, c, x[ 5], 12, 0x4787c62a);
	FF(c, d, a, b, x[ 6], 17, 0xa8304613);
	FF(b, c, d, a, x[ 7], 22, 0xfd469501);
	FF(a, b, c, d, x[ 8], 7, 0x698098d8);
	FF(d, a, b, c, x[ 9], 12, 0x8b44f7af);
	FF(c, d, a, b, x[10], 17, 0xffff5bb1);
	FF(b, c, d, a, x[11], 22, 0x895cd7be);
	FF(a, b, c, d, x[12], 7, 0x6b901122);
	FF(d, a, b, c, x[13], 12, 0xfd987193);
	FF(c, d, a, b, x[14], 17, 0xa679438e);
	FF(b, c, d, a, x[15], 22, 0x49b40821);

	GG(a, b, c, d, x[ 1], 5, 0xf61e2562);
	GG(d, a, b, c, x[ 6], 9, 0xc040b340);
	GG(c, d, a, b, x[11], 14, 0x265e5a51);
	GG(b, c, d, a, x[ 0], 20, 0xe9b6c7aa);
	GG(a, b, c, d, x[ 5], 5, 0xd62f105d);
	GG(d, a, b, c, x[10], 9,  0x2441453);
	GG(c, d, a, b, x[15], 14, 0xd8a1e681);
	GG(b, c, d, a, x[ 4], 20, 0xe7d3fbc8);
	GG(a, b, c, d, x[ 9], 5, 0x21e1cde6);
	GG(d, a, b, c, x[14], 9, 0xc33707d6);
	GG(c, d, a, b, x[ 3], 14, 0xf4d50d87);
	GG(b, c, d, a, x[ 8], 20, 0x455a14ed);
	GG(a, b, c, d, x[13], 5, 0xa9e3e905);
	GG(d, a, b, c, x[ 2], 9, 0xfcefa3f8);
	GG(c, d, a, b, x[ 7], 14, 0x676f02d9);
	GG(b, c, d, a, x[12], 20, 0x8d2a4c8a);


	HH(a, b, c, d, x[ 5], 4, 0xfffa3942);
	HH(d, a, b, c, x[ 8], 11, 0x8771f681);
	HH(c, d, a, b, x[11], 16, 0x6d9d6122);
	HH(b, c, d, a, x[14], 23, 0xfde5380c);
	HH(a, b, c, d, x[ 1], 4, 0xa4beea44);
	HH(d, a, b, c, x[ 4], 11, 0x4bdecfa9);
	HH(c, d, a, b, x[ 7], 16, 0xf6bb4b60);
	HH(b, c, d, a, x[10], 23, 0xbebfbc70);
	HH(a, b, c, d, x[13], 4, 0x289b7ec6);
	HH(d, a, b, c, x[ 0], 11, 0xeaa127fa);
	HH(c, d, a, b, x[ 3], 16, 0xd4ef3085);
	HH(b, c, d, a, x[ 6], 23,  0x4881d05);
	HH(a, b, c, d, x[ 9], 4, 0xd9d4d039);
	HH(d, a, b, c, x[12], 11, 0xe6db99e5);
	HH(c, d, a, b, x[15], 16, 0x1fa27cf8);
	HH(b, c, d, a, x[ 2], 23, 0xc4ac5665);


	II(a, b, c, d, x[ 0], 6, 0xf4292244);
	II(d, a, b, c, x[ 7], 10, 0x432aff97);
	II(c, d, a, b, x[14], 15, 0xab9423a7);
	II(b, c, d, a, x[ 5], 21, 0xfc93a039);
	II(a, b, c, d, x[12], 6, 0x655b59c3);
	II(d, a, b, c, x[ 3], 10, 0x8f0ccc92);
	II(c, d, a, b, x[10], 15, 0xffeff47d);
	II(b, c, d, a, x[ 1], 21, 0x85845dd1);
	II(a, b, c, d, x[ 8], 6, 0x6fa87e4f);
	II(d, a, b, c, x[15], 10, 0xfe2ce6e0);
	II(c, d, a, b, x[ 6], 15, 0xa3014314);
	II(b, c, d, a, x[13], 21, 0x4e0811a1);
	II(a, b, c, d, x[ 4], 6, 0xf7537e82);
	II(d, a, b, c, x[11], 10, 0xbd3af235);
	II(c, d, a, b, x[ 2], 15, 0x2ad7d2bb);
	II(b, c, d, a, x[ 9], 21, 0xeb86d391);
	state[0] += a;
	state[1] += b;
	state[2] += c;
	state[3] += d;
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`

**Document**:

> ### void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)
> 将输入的字节数组解码为无符号整数数组。
> 
> #### Parameters
> - output: 指向无符号整数数组的指针，用于存储解码后的结果。
> - input: 指向字节数组的指针，包含待解码的数据。
> - len: 输入字节数组的长度（以字节为单位）。
> 
> #### Code Details
> `MD5Decode` 方法的主要功能是将输入的字节数组 `input` 解码为无符号整数数组 `output`。该方法通过逐个读取每四个字节并将其组合成一个无符号整数来实现这一目标。具体步骤如下：
> 
> 1. 初始化两个索引变量 `i` 和 `j`，分别用于跟踪 `output` 数组和 `input` 数组的位置。
> 2. 使用 `while` 循环遍历 `input` 数组，直到处理完所有字节（即 `j < len`）。
> 3. 在每次循环中，从 `input` 数组中读取四个连续的字节，并将它们组合成一个无符号整数：
>    - 第一个字节直接赋值给最低有效字节 (LSB)。
>    - 第二个字节左移 8 位后与第一个字节进行按位或操作。
>    - 第三个字节左移 16 位后与前两个字节的结果进行按位或操作。
>    - 第四个字节左移 24 位后与前三个字节的结果进行按位或操作。
> 4. 将组合后的无符号整数存储到 `output` 数组中。
> 5. 更新索引变量 `i` 和 `j`，以便在下一次循环中处理下一个四字节块。
> 
> 需要注意的是，该方法假设 `len` 是 4 的倍数。如果 `len` 不是 4 的倍数，则可能会导致未定义行为。
> 
> #### Example
> ```C++
> #include "md5.h"
> 
> int main() {
>     unsigned char input[] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF};
>     unsigned int output[2];
>     unsigned int len = sizeof(input);
> 
>     MD5Decode(output, input, len);
> 
>     // 输出解码后的结果
>     for (int i = 0; i < 2; i++) {
>         printf("Output[%d] = 0x%08X\n", i, output[i]);
>     }
> 
>     return 0;
> }
> ```
> 
> 此示例展示了如何使用 `MD5Decode` 方法将一个包含 8 个字节的数组解码为两个无符号整数，并打印解码后的结果。
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`.

The code of the Method is as follows:

```C++
void MD5Decode(unsigned int *output,unsigned char *input,unsigned int len) {
	unsigned int i = 0,j = 0;
	while(j < len) {
		output[i] = (input[j]) | (input[j+1] << 8) | (input[j+2] << 16) | (input[j+3] << 24);
		i++;
		j+=4;
	}
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. 
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Transform(unsigned int [4] state, unsigned char [64] block)`.

The code of the Method is as follows:

```C++
void MD5Transform(unsigned int state[4],unsigned char block[64]) {
	unsigned int a = state[0];
	unsigned int b = state[1];
	unsigned int c = state[2];
	unsigned int d = state[3];
	unsigned int x[64];

	MD5Decode(x,block,64);

	FF(a, b, c, d, x[ 0], 7, 0xd76aa478);
	FF(d, a, b, c, x[ 1], 12, 0xe8c7b756);
	FF(c, d, a, b, x[ 2], 17, 0x242070db);
	FF(b, c, d, a, x[ 3], 22, 0xc1bdceee);
	FF(a, b, c, d, x[ 4], 7, 0xf57c0faf);
	FF(d, a, b, c, x[ 5], 12, 0x4787c62a);
	FF(c, d, a, b, x[ 6], 17, 0xa8304613);
	FF(b, c, d, a, x[ 7], 22, 0xfd469501);
	FF(a, b, c, d, x[ 8], 7, 0x698098d8);
	FF(d, a, b, c, x[ 9], 12, 0x8b44f7af);
	FF(c, d, a, b, x[10], 17, 0xffff5bb1);
	FF(b, c, d, a, x[11], 22, 0x895cd7be);
	FF(a, b, c, d, x[12], 7, 0x6b901122);
	FF(d, a, b, c, x[13], 12, 0xfd987193);
	FF(c, d, a, b, x[14], 17, 0xa679438e);
	FF(b, c, d, a, x[15], 22, 0x49b40821);

	GG(a, b, c, d, x[ 1], 5, 0xf61e2562);
	GG(d, a, b, c, x[ 6], 9, 0xc040b340);
	GG(c, d, a, b, x[11], 14, 0x265e5a51);
	GG(b, c, d, a, x[ 0], 20, 0xe9b6c7aa);
	GG(a, b, c, d, x[ 5], 5, 0xd62f105d);
	GG(d, a, b, c, x[10], 9,  0x2441453);
	GG(c, d, a, b, x[15], 14, 0xd8a1e681);
	GG(b, c, d, a, x[ 4], 20, 0xe7d3fbc8);
	GG(a, b, c, d, x[ 9], 5, 0x21e1cde6);
	GG(d, a, b, c, x[14], 9, 0xc33707d6);
	GG(c, d, a, b, x[ 3], 14, 0xf4d50d87);
	GG(b, c, d, a, x[ 8], 20, 0x455a14ed);
	GG(a, b, c, d, x[13], 5, 0xa9e3e905);
	GG(d, a, b, c, x[ 2], 9, 0xfcefa3f8);
	GG(c, d, a, b, x[ 7], 14, 0x676f02d9);
	GG(b, c, d, a, x[12], 20, 0x8d2a4c8a);


	HH(a, b, c, d, x[ 5], 4, 0xfffa3942);
	HH(d, a, b, c, x[ 8], 11, 0x8771f681);
	HH(c, d, a, b, x[11], 16, 0x6d9d6122);
	HH(b, c, d, a, x[14], 23, 0xfde5380c);
	HH(a, b, c, d, x[ 1], 4, 0xa4beea44);
	HH(d, a, b, c, x[ 4], 11, 0x4bdecfa9);
	HH(c, d, a, b, x[ 7], 16, 0xf6bb4b60);
	HH(b, c, d, a, x[10], 23, 0xbebfbc70);
	HH(a, b, c, d, x[13], 4, 0x289b7ec6);
	HH(d, a, b, c, x[ 0], 11, 0xeaa127fa);
	HH(c, d, a, b, x[ 3], 16, 0xd4ef3085);
	HH(b, c, d, a, x[ 6], 23,  0x4881d05);
	HH(a, b, c, d, x[ 9], 4, 0xd9d4d039);
	HH(d, a, b, c, x[12], 11, 0xe6db99e5);
	HH(c, d, a, b, x[15], 16, 0x1fa27cf8);
	HH(b, c, d, a, x[ 2], 23, 0xc4ac5665);


	II(a, b, c, d, x[ 0], 6, 0xf4292244);
	II(d, a, b, c, x[ 7], 10, 0x432aff97);
	II(c, d, a, b, x[14], 15, 0xab9423a7);
	II(b, c, d, a, x[ 5], 21, 0xfc93a039);
	II(a, b, c, d, x[12], 6, 0x655b59c3);
	II(d, a, b, c, x[ 3], 10, 0x8f0ccc92);
	II(c, d, a, b, x[10], 15, 0xffeff47d);
	II(b, c, d, a, x[ 1], 21, 0x85845dd1);
	II(a, b, c, d, x[ 8], 6, 0x6fa87e4f);
	II(d, a, b, c, x[15], 10, 0xfe2ce6e0);
	II(c, d, a, b, x[ 6], 15, 0xa3014314);
	II(b, c, d, a, x[13], 21, 0x4e0811a1);
	II(a, b, c, d, x[ 4], 6, 0xf7537e82);
	II(d, a, b, c, x[11], 10, 0xbd3af235);
	II(c, d, a, b, x[ 2], 15, 0x2ad7d2bb);
	II(b, c, d, a, x[ 9], 21, 0xeb86d391);
	state[0] += a;
	state[1] += b;
	state[2] += c;
	state[3] += d;
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`

**Document**:

> ### void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)
> #### Description
> 该方法用于将字节数组 `input` 解码为整数数组 `output`。它每次从 `input` 中读取 4 个字节，并将其组合成一个 `unsigned int` 值，然后存储到 `output` 数组中。
> 
> #### Parameters
> - `output`: 指向 `unsigned int` 类型数组的指针，用于存储解码后的结果。
> - `input`: 指向 `unsigned char` 类型数组的指针，包含待解码的字节数据。
> - `len`: 表示 `input` 数组中有效字节的长度。
> 
> #### Code Details
> 该方法通过循环遍历 `input` 数组，每次处理 4 个字节，并将这 4 个字节组合成一个 `unsigned int` 值，然后存储到 `output` 数组中。具体步骤如下：
> 
> 1. 初始化两个索引变量 `i` 和 `j`，分别用于跟踪 `output` 和 `input` 数组中的位置。
> 2. 使用 `while` 循环遍历 `input` 数组，直到处理完所有指定长度的字节。
> 3. 在每次循环中，从 `input[j]` 开始读取 4 个字节，并通过位运算将其组合成一个 `unsigned int` 值：
>    - `input[j]` 是最低有效字节 (Least Significant Byte, LSB)。
>    - `input[j+1] << 8` 将第二个字节左移 8 位。
>    - `input[j+2] << 16` 将第三个字节左移 16 位。
>    - `input[j+3] << 24` 将第四个字节左移 24 位。
> 4. 将组合后的 `unsigned int` 值存储到 `output[i]` 中。
> 5. 更新索引 `i` 和 `j`，继续处理下一个 4 字节块。
> 
> 需要注意的是，`len` 必须是 4 的倍数，否则会导致未定义行为或数组越界错误。
> 
> #### Example
> ```C++
> #include <stdio.h>
> 
> void MD5Decode(unsigned int *output, unsigned char *input, unsigned int len);
> 
> int main() {
>     unsigned char input[] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF};
>     unsigned int output[2];
>     unsigned int len = sizeof(input);
> 
>     MD5Decode(output, input, len);
> 
>     printf("Decoded values:\n");
>     for (int i = 0; i < 2; ++i) {
>         printf("output[%d] = 0x%08X\n", i, output[i]);
>     }
> 
>     return 0;
> }
> ```
> 
> 在上述示例中，`input` 数组包含 8 个字节的数据，`MD5Decode` 方法将其解码为两个 `unsigned int` 值并存储在 `output` 数组中。
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)`.

The code of the Method is as follows:

```C++
void MD5Update(MD5_CTX *context,unsigned char *input,unsigned int inputlen)
{
	unsigned int i = 0,index = 0,partlen = 0;
	index = (context->count[0] >> 3) & 0x3F;
	partlen = 64 - index;
	context->count[0] += inputlen << 3;
	if(context->count[0] < (inputlen << 3)) {
		context->count[1]++;
	}
	context->count[1] += inputlen >> 29;

	if(inputlen >= partlen) {
		memcpy(&context->buffer[index],input,partlen);
		MD5Transform(context->state,context->buffer);
		for(i = partlen;i+64 <= inputlen;i+=64) {
			MD5Transform(context->state,&input[i]);
		}
		index = 0;
	} else {
		i = 0;
	}
	
	memcpy(&context->buffer[index],&input[i],inputlen-i);
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Transform(unsigned int [4] state, unsigned char [64] block)`

**Document**:

> ### void MD5Transform(unsigned int [4] state, unsigned char [64] block)
> #### Description
> 该方法用于对给定的 64 字节块进行 MD5 转换，并更新状态向量 `state`。它是 MD5 哈希算法的核心部分，负责处理每个 512 位（64 字节）的数据块。
> 
> #### Parameters
> - `state`: 指向包含 4 个 `unsigned int` 类型元素的数组的指针，表示当前的哈希状态。
> - `block`: 指向包含 64 个 `unsigned char` 类型元素的数组的指针，表示待处理的 64 字节数据块。
> 
> #### Code Details
> `MD5Transform` 方法的主要功能是根据 MD5 算法的标准流程对输入的 64 字节数据块进行处理，并更新状态向量 `state`。具体步骤如下：
> 
> 1. **初始化变量**：
>    - 将 `state` 数组中的值分别赋给局部变量 `a`, `b`, `c`, `d`。
>    - 创建一个长度为 64 的 `unsigned int` 数组 `x`，用于存储解码后的数据块。
> 
> 2. **解码数据块**：
>    - 调用 `MD5Decode` 方法将 `block` 中的 64 个字节解码为 16 个 `unsigned int` 值，并存储到 `x` 数组中。这一步骤确保了数据块可以被正确地处理为整数形式。
> 
> 3. **执行 MD5 核心变换**：
>    - 使用四个不同的函数 `FF`, `GG`, `HH`, `II` 对 `x` 数组中的数据进行处理。这些函数实现了 MD5 算法中的不同轮次变换，每一轮使用不同的常量和旋转位移。
>    - 每个函数调用都传递了当前的状态变量 `a`, `b`, `c`, `d`，以及从 `x` 数组中选择的数据项、旋转位移量和一个常量值。
>    - 这些函数的具体实现不在本方法中，但它们共同作用以确保数据块经过复杂的非线性变换后能够产生新的状态值。
> 
> 4. **更新状态向量**：
>    - 在所有轮次变换完成后，将局部变量 `a`, `b`, `c`, `d` 的新值加回到 `state` 数组中，从而更新哈希状态。
> 
> #### Example
> ```C++
> #include <stdio.h>
> 
> void MD5Transform(unsigned int state[4], unsigned char block[64]);
> void MD5Decode(unsigned int *output, unsigned char *input, unsigned int len);
> 
> int main() {
>     unsigned int state[4] = {0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476};
>     unsigned char block[64] = {
>         // 示例数据块，实际应用中应为有效的 64 字节数据
>         0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF,
>         0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10,
>         // ... 其余 48 字节 ...
>     };
> 
>     MD5Transform(state, block);
> 
>     printf("Updated state:\n");
>     for (int i = 0; i < 4; ++i) {
>         printf("state[%d] = 0x%08X\n", i, state[i]);
>     }
> 
>     return 0;
> }
> ```
> 
> 在上述示例中，`state` 数组初始化为 MD5 算法的标准初始值，`block` 数组包含 64 个字节的数据。调用 `MD5Transform` 方法后，`state` 数组将被更新为新的哈希状态。
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Encode(unsigned char * output, unsigned int * input, unsigned int len)`.

The code of the Method is as follows:

```C++
void MD5Encode(unsigned char *output,unsigned int *input,unsigned int len) {
	unsigned int i = 0,j = 0;
	while(j < len) {
		output[j] = input[i] & 0xFF;
		output[j+1] = (input[i] >> 8) & 0xFF;
		output[j+2] = (input[i] >> 16) & 0xFF;
		output[j+3] = (input[i] >> 24) & 0xFF;
		i++;
		j+=4;
	}
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. 
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Final(MD5_CTX * context, unsigned char [16] digest)`.

The code of the Method is as follows:

```C++
void MD5Final(MD5_CTX *context,unsigned char digest[16]) {
	unsigned int index = 0,padlen = 0;
	unsigned char bits[8];
	index = (context->count[0] >> 3) & 0x3F;
	padlen = (index < 56)?(56-index):(120-index);
	MD5Encode(bits,context->count,8);
	MD5Update(context,PADDING,padlen);
	MD5Update(context,bits,8);
	MD5Encode(digest,context->state,16);
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Encode(unsigned char * output, unsigned int * input, unsigned int len)`

**Document**:

> ### void MD5Encode(unsigned char * output, unsigned int * input, unsigned int len)
> #### Description
> 该函数 `MD5Encode` 用于将一个无符号整数数组 `input` 编码为一个无符号字符数组 `output`。每个无符号整数（32位）会被拆分为4个字节，并依次存储到 `output` 中。
> 
> #### Parameters
> - `output`: 指向目标缓冲区的指针，用于存储编码后的结果。
> - `input`: 指向源数据的指针，包含需要编码的无符号整数数组。
> - `len`: 输入数组 `input` 的长度（以无符号整数为单位），即需要处理的元素个数。
> 
> #### Code Details
> 该函数通过遍历输入数组 `input` 并逐个处理每个无符号整数来实现编码。具体步骤如下：
> 
> 1. 初始化两个索引变量 `i` 和 `j`，分别用于遍历 `input` 和 `output` 数组。
> 2. 使用 `while` 循环遍历 `input` 数组中的每个元素，直到处理完所有元素（即 `j < len`）。
> 3. 对于每个 `input[i]`：
>    - `output[j] = input[i] & 0xFF;`：提取最低的8位并存储到 `output[j]`。
>    - `output[j+1] = (input[i] >> 8) & 0xFF;`：右移8位后提取最低的8位并存储到 `output[j+1]`。
>    - `output[j+2] = (input[i] >> 16) & 0xFF;`：右移16位后提取最低的8位并存储到 `output[j+2]`。
>    - `output[j+3] = (input[i] >> 24) & 0xFF;`：右移24位后提取最低的8位并存储到 `output[j+3]`。
> 4. 每次处理完一个 `input[i]` 后，`i` 增加1，`j` 增加4，以便处理下一个整数和对应的四个字节。
> 
> #### Example
> ```C++
> #include "md5.h"
> 
> int main() {
>     unsigned int input[] = {0x12345678, 0x9ABCDEF0};
>     unsigned char output[8];
>     unsigned int len = sizeof(input) / sizeof(unsigned int);
> 
>     MD5Encode(output, input, len);
> 
>     for (int i = 0; i < 8; ++i) {
>         printf("%02X ", output[i]);
>     }
> 
>     return 0;
> }
> ```
> 
> 此示例代码展示了如何使用 `MD5Encode` 函数将一个包含两个无符号整数的数组编码为一个字符数组，并打印出编码后的结果。
---
**Method**: `void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)`

**Document**:

> ### void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)
> #### Description
> 该方法用于更新 MD5 哈希上下文，处理输入的数据块，并根据需要调用 `MD5Transform` 方法进行哈希变换。它是 MD5 哈希算法中处理数据的核心部分。
> 
> #### Parameters
> - `context`: 指向 `MD5_CTX` 结构的指针，表示当前的 MD5 哈希上下文。
> - `input`: 指向包含待处理数据的 `unsigned char` 数组的指针。
> - `inputlen`: 表示 `input` 数组中数据的长度（以字节为单位）。
> 
> #### Code Details
> `MD5Update` 方法的主要功能是将输入的数据块添加到当前的 MD5 哈希上下文中，并根据需要调用 `MD5Transform` 方法对 64 字节的数据块进行哈希变换。具体步骤如下：
> 
> 1. **初始化变量**：
>    - `index`：计算当前缓冲区中已填充的字节数（0 到 63），即 `context->count[0]` 的低 6 位。
>    - `partlen`：计算剩余可填充的字节数，即 `64 - index`。
>    - 更新 `context->count`，记录处理的总字节数（以比特为单位）。如果处理的字节数超过 2^32 比特，则更新 `context->count[1]`。
> 
> 2. **处理输入数据**：
>    - 如果 `inputlen` 大于或等于 `partlen`，则先将剩余空间填满并调用 `MD5Transform` 进行哈希变换。
>    - 然后，对于每 64 字节的数据块，直接调用 `MD5Transform` 进行哈希变换。
>    - 最后，将剩余不足 64 字节的数据复制到缓冲区中。
> 
> 3. **更新缓冲区**：
>    - 将剩余的数据复制到 `context->buffer` 中，等待下一次调用时继续处理。
> 
> #### Example
> ```C++
> #include <stdio.h>
> #include "md5.h"
> 
> int main() {
>     MD5_CTX context;
>     unsigned char input[] = "Hello, World!";
>     unsigned int inputlen = sizeof(input) - 1; // 不包括终止符
> 
>     MD5Init(&context);
>     MD5Update(&context, input, inputlen);
> 
>     unsigned char digest[16];
>     MD5Final(digest, &context);
> 
>     printf("MD5 Digest: ");
>     for (int i = 0; i < 16; ++i) {
>         printf("%02x", digest[i]);
>     }
>     printf("\n");
> 
>     return 0;
> }
> ```
> 
> 在上述示例中，`MD5Update` 方法被用于更新 MD5 哈希上下文，处理输入字符串 `"Hello, World!"`。最终通过 `MD5Final` 方法获取哈希结果并打印出来。
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Init(MD5_CTX * context)`.

The code of the Method is as follows:

```C++
void MD5Init(MD5_CTX *context) {
	context->count[0] = 0;
	context->count[1] = 0;
	context->state[0] = 0x67452301;
	context->state[1] = 0xEFCDAB89;
	context->state[2] = 0x98BADCFE;
	context->state[3] = 0x10325476;
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. 
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is main.c.
Now you need to generate a document for a Method, whose name is `int main(int argc, char *[] argv)`.

The code of the Method is as follows:

```C++
int main(int argc, char *argv[]) {
	int i, n;
	bool isfile = false;
	unsigned char decrypt[16];
	MD5_CTX md5;
	
	if(argc > 1 && strlen(argv[1]) == 2 && !memcmp(argv[1], "-f", 2)) {
		isfile = true;
	}
	
	if(argc == 1 || (argc == 2 && isfile)) {
		fprintf(stderr, "usage:\n    %s -f file ...\n    %s string ...\n", argv[0], argv[0]);
		return 1;
	}
	
	if(isfile) {
		FILE *fp;
		for(n=2; n<argc; n++) {
			fp = fopen(argv[n], "rb");
			if(fp == NULL) {
				fprintf(stderr, "File %s not exists, errno = %d, error = %s\n", argv[n], errno, strerror(errno));
				continue;
			}
			
			MD5Init(&md5);
			
			do {
				unsigned char encrypt[1024];
				while(!feof(fp)) {
					MD5Update(&md5, encrypt, fread(encrypt, 1, sizeof(encrypt), fp));
				}
				fclose(fp);
			} while(0);
			
			MD5Final(&md5, decrypt);

			for(i=0; i<16; i++) {
				printf("%02x", decrypt[i]);  //02x前需要加上 %
			}
			
			printf("  %s\n", argv[n]);
		}
	} else {
		for(n=1; n<argc; n++) {
			MD5Init(&md5);
			MD5Update(&md5, argv[n], strlen(argv[n]));
			MD5Final(&md5, decrypt);

			for(i=0; i<16; i++) {
				printf("%02x", decrypt[i]);  //02x前需要加上 %
			}
			
			printf("  %s\n", argv[n]);
		}
	}

	return 0;
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Init(MD5_CTX * context)`

**Document**:

> ### void MD5Init(MD5_CTX * context)
> #### Description
> 初始化 MD5 上下文，设置初始状态和计数器。
> 
> #### Parameters
> - `context`: 指向 MD5_CTX 结构的指针，用于存储 MD5 算法的状态和计数信息。
> 
> #### Code Details
> `MD5Init` 方法用于初始化一个 MD5 上下文对象。具体来说，它执行以下操作：
> 
> 1. 将 `context->count[0]` 和 `context->count[1]` 设置为 0。这两个变量用于记录处理的消息长度（以比特为单位），其中 `count[0]` 存储低 32 位，`count[1]` 存储高 32 位。
> 2. 初始化 `context->state` 数组中的四个元素，这些元素是 MD5 算法的初始状态值：
>    - `context->state[0]` 被设置为 `0x67452301`
>    - `context->state[1]` 被设置为 `0xEFCDAB89`
>    - `context->state[2]` 被设置为 `0x98BADCFE`
>    - `context->state[3]` 被设置为 `0x10325476`
> 
> 这些初始状态值是 MD5 算法标准中定义的常量，确保每次初始化时 MD5 上下文处于一致的状态。
> 
> #### Example
> ```C++
> #include "md5.h"
> 
> int main() {
>     MD5_CTX context;
>     MD5Init(&context);
>     // 继续使用已初始化的 context 进行其他 MD5 操作
>     return 0;
> }
> ```
---
**Method**: `void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)`

**Document**:

> ### void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)
> #### Description
> 该方法用于更新 MD5 哈希上下文，处理输入的数据块，并根据需要调用 `MD5Transform` 方法进行哈希变换。它是 MD5 哈希算法中处理数据的核心部分。
> 
> #### Parameters
> - `context`: 指向 `MD5_CTX` 结构的指针，表示当前的 MD5 哈希上下文。
> - `input`: 指向包含待处理数据的 `unsigned char` 数组的指针。
> - `inputlen`: 表示 `input` 数组中数据的长度（以字节为单位）。
> 
> #### Code Details
> `MD5Update` 方法的主要功能是将输入的数据块添加到当前的 MD5 哈希上下文中，并根据需要调用 `MD5Transform` 方法对 64 字节的数据块进行哈希变换。具体步骤如下：
> 
> 1. **初始化变量**：
>    - `index`：计算当前缓冲区中已填充的字节数（0 到 63），即 `context->count[0]` 的低 6 位。
>    - `partlen`：计算剩余可填充的字节数，即 `64 - index`。
>    - 更新 `context->count`，记录处理的总字节数（以比特为单位）。如果处理的字节数超过 2^32 比特，则更新 `context->count[1]`。
> 
> 2. **处理输入数据**：
>    - 如果 `inputlen` 大于或等于 `partlen`，则先将剩余空间填满并调用 `MD5Transform` 进行哈希变换。
>    - 然后，对于每 64 字节的数据块，直接调用 `MD5Transform` 进行哈希变换。
>    - 最后，将剩余不足 64 字节的数据复制到缓冲区中。
> 
> 3. **更新缓冲区**：
>    - 将剩余的数据复制到 `context->buffer` 中，等待下一次调用时继续处理。
> 
> #### Example
> ```C++
> #include <stdio.h>
> #include "md5.h"
> 
> int main() {
>     MD5_CTX context;
>     unsigned char input[] = "Hello, World!";
>     unsigned int inputlen = sizeof(input) - 1; // 不包括终止符
> 
>     MD5Init(&context);
>     MD5Update(&context, input, inputlen);
> 
>     unsigned char digest[16];
>     MD5Final(digest, &context);
> 
>     printf("MD5 Digest: ");
>     for (int i = 0; i < 16; ++i) {
>         printf("%02x", digest[i]);
>     }
>     printf("\n");
> 
>     return 0;
> }
> ```
> 
> 在上述示例中，`MD5Update` 方法被用于更新 MD5 哈希上下文，处理输入字符串 `"Hello, World!"`。最终通过 `MD5Final` 方法获取哈希结果并打印出来。
---
**Method**: `void MD5Final(MD5_CTX * context, unsigned char [16] digest)`

**Document**:

> ### void MD5Final(MD5_CTX * context, unsigned char [16] digest)
> #### Description
> 该函数 `MD5Final` 用于完成 MD5 哈希计算，并将最终的哈希值存储到指定的缓冲区中。
> 
> #### Parameters
> - `context`: 指向 `MD5_CTX` 结构的指针，表示当前的 MD5 哈希上下文。
> - `digest`: 指向一个长度为 16 的无符号字符数组的指针，用于存储最终的 MD5 哈希值。
> 
> #### Code Details
> `MD5Final` 函数的主要功能是完成 MD5 哈希计算的最后一步。具体步骤如下：
> 
> 1. **计算填充长度**：
>    - 计算当前缓冲区中已填充的字节数 `index`，即 `(context->count[0] >> 3) & 0x3F`。
>    - 根据 `index` 计算需要填充的字节数 `padlen`。如果 `index` 小于 56，则填充到 56 字节；否则填充到 120 字节（即下一个 64 字节块的开始）。
> 
> 2. **编码消息长度**：
>    - 使用 `MD5Encode` 函数将 `context->count` 编码为 8 字节的字符数组 `bits`，表示处理的消息总长度（以比特为单位）。
> 
> 3. **更新哈希上下文**：
>    - 使用 `MD5Update` 函数将填充数据 `PADDING` 和消息长度 `bits` 添加到哈希上下文中。这确保了哈希计算的完整性。
> 
> 4. **生成最终哈希值**：
>    - 使用 `MD5Encode` 函数将 `context->state` 编码为 16 字节的字符数组 `digest`，表示最终的 MD5 哈希值。
> 
> 通过这些步骤，`MD5Final` 确保了 MD5 哈希计算的完整性和正确性。它依赖于 `MD5Encode` 和 `MD5Update` 函数来完成具体的编码和更新操作。
> 
> #### Example
> ```C++
> #include <stdio.h>
> #include "md5.h"
> 
> int main() {
>     MD5_CTX context;
>     unsigned char input[] = "Hello, World!";
>     unsigned int inputlen = sizeof(input) - 1; // 不包括终止符
> 
>     MD5Init(&context);
>     MD5Update(&context, input, inputlen);
> 
>     unsigned char digest[16];
>     MD5Final(digest, &context);
> 
>     printf("MD5 Digest: ");
>     for (int i = 0; i < 16; ++i) {
>         printf("%02x", digest[i]);
>     }
>     printf("\n");
> 
>     return 0;
> }
> ```
> 
> 在上述示例中，`MD5Final` 方法被用于完成 MD5 哈希计算，并将最终的哈希值存储到 `digest` 数组中。最终通过打印 `digest` 数组中的值来展示哈希结果。
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in 中文 though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`.

The code of the Method is as follows:

```C++
void MD5Decode(unsigned int *output,unsigned char *input,unsigned int len) {
	unsigned int i = 0,j = 0;
	while(j < len) {
		output[i] = (input[j]) | (input[j+1] << 8) | (input[j+2] << 16) | (input[j+3] << 24);
		i++;
		j+=4;
	}
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. 
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Transform(unsigned int [4] state, unsigned char [64] block)`.

The code of the Method is as follows:

```C++
void MD5Transform(unsigned int state[4],unsigned char block[64]) {
	unsigned int a = state[0];
	unsigned int b = state[1];
	unsigned int c = state[2];
	unsigned int d = state[3];
	unsigned int x[64];

	MD5Decode(x,block,64);

	FF(a, b, c, d, x[ 0], 7, 0xd76aa478);
	FF(d, a, b, c, x[ 1], 12, 0xe8c7b756);
	FF(c, d, a, b, x[ 2], 17, 0x242070db);
	FF(b, c, d, a, x[ 3], 22, 0xc1bdceee);
	FF(a, b, c, d, x[ 4], 7, 0xf57c0faf);
	FF(d, a, b, c, x[ 5], 12, 0x4787c62a);
	FF(c, d, a, b, x[ 6], 17, 0xa8304613);
	FF(b, c, d, a, x[ 7], 22, 0xfd469501);
	FF(a, b, c, d, x[ 8], 7, 0x698098d8);
	FF(d, a, b, c, x[ 9], 12, 0x8b44f7af);
	FF(c, d, a, b, x[10], 17, 0xffff5bb1);
	FF(b, c, d, a, x[11], 22, 0x895cd7be);
	FF(a, b, c, d, x[12], 7, 0x6b901122);
	FF(d, a, b, c, x[13], 12, 0xfd987193);
	FF(c, d, a, b, x[14], 17, 0xa679438e);
	FF(b, c, d, a, x[15], 22, 0x49b40821);

	GG(a, b, c, d, x[ 1], 5, 0xf61e2562);
	GG(d, a, b, c, x[ 6], 9, 0xc040b340);
	GG(c, d, a, b, x[11], 14, 0x265e5a51);
	GG(b, c, d, a, x[ 0], 20, 0xe9b6c7aa);
	GG(a, b, c, d, x[ 5], 5, 0xd62f105d);
	GG(d, a, b, c, x[10], 9,  0x2441453);
	GG(c, d, a, b, x[15], 14, 0xd8a1e681);
	GG(b, c, d, a, x[ 4], 20, 0xe7d3fbc8);
	GG(a, b, c, d, x[ 9], 5, 0x21e1cde6);
	GG(d, a, b, c, x[14], 9, 0xc33707d6);
	GG(c, d, a, b, x[ 3], 14, 0xf4d50d87);
	GG(b, c, d, a, x[ 8], 20, 0x455a14ed);
	GG(a, b, c, d, x[13], 5, 0xa9e3e905);
	GG(d, a, b, c, x[ 2], 9, 0xfcefa3f8);
	GG(c, d, a, b, x[ 7], 14, 0x676f02d9);
	GG(b, c, d, a, x[12], 20, 0x8d2a4c8a);


	HH(a, b, c, d, x[ 5], 4, 0xfffa3942);
	HH(d, a, b, c, x[ 8], 11, 0x8771f681);
	HH(c, d, a, b, x[11], 16, 0x6d9d6122);
	HH(b, c, d, a, x[14], 23, 0xfde5380c);
	HH(a, b, c, d, x[ 1], 4, 0xa4beea44);
	HH(d, a, b, c, x[ 4], 11, 0x4bdecfa9);
	HH(c, d, a, b, x[ 7], 16, 0xf6bb4b60);
	HH(b, c, d, a, x[10], 23, 0xbebfbc70);
	HH(a, b, c, d, x[13], 4, 0x289b7ec6);
	HH(d, a, b, c, x[ 0], 11, 0xeaa127fa);
	HH(c, d, a, b, x[ 3], 16, 0xd4ef3085);
	HH(b, c, d, a, x[ 6], 23,  0x4881d05);
	HH(a, b, c, d, x[ 9], 4, 0xd9d4d039);
	HH(d, a, b, c, x[12], 11, 0xe6db99e5);
	HH(c, d, a, b, x[15], 16, 0x1fa27cf8);
	HH(b, c, d, a, x[ 2], 23, 0xc4ac5665);


	II(a, b, c, d, x[ 0], 6, 0xf4292244);
	II(d, a, b, c, x[ 7], 10, 0x432aff97);
	II(c, d, a, b, x[14], 15, 0xab9423a7);
	II(b, c, d, a, x[ 5], 21, 0xfc93a039);
	II(a, b, c, d, x[12], 6, 0x655b59c3);
	II(d, a, b, c, x[ 3], 10, 0x8f0ccc92);
	II(c, d, a, b, x[10], 15, 0xffeff47d);
	II(b, c, d, a, x[ 1], 21, 0x85845dd1);
	II(a, b, c, d, x[ 8], 6, 0x6fa87e4f);
	II(d, a, b, c, x[15], 10, 0xfe2ce6e0);
	II(c, d, a, b, x[ 6], 15, 0xa3014314);
	II(b, c, d, a, x[13], 21, 0x4e0811a1);
	II(a, b, c, d, x[ 4], 6, 0xf7537e82);
	II(d, a, b, c, x[11], 10, 0xbd3af235);
	II(c, d, a, b, x[ 2], 15, 0x2ad7d2bb);
	II(b, c, d, a, x[ 9], 21, 0xeb86d391);
	state[0] += a;
	state[1] += b;
	state[2] += c;
	state[3] += d;
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`

**Document**:

> ### void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)
> #### Description
> 该方法用于将一个字节数组解码为一个整数数组。具体来说，它将输入的字节数组每四个字节转换为一个无符号整数，并依次存储到输出数组中。
> 
> #### Parameters
> - `output`: 一个指向无符号整数数组的指针，用于存储解码后的结果。
> - `input`: 一个指向字节数组的指针，包含待解码的数据。
> - `len`: 输入字节数组的长度（以字节为单位）。
> 
> #### Code Details
> 详细分析如下：
> 
> 1. **初始化索引变量**：
>    ```C++
>    unsigned int i = 0, j = 0;
>    ```
>    这里定义了两个索引变量 `i` 和 `j`，分别用于遍历 `output` 和 `input` 数组。
> 
> 2. **循环处理输入数据**：
>    ```C++
>    while (j < len) {
>        output[i] = (input[j]) | (input[j+1] << 8) | (input[j+2] << 16) | (input[j+3] << 24);
>        i++;
>        j += 4;
>    }
>    ```
>    - 循环条件是 `j` 小于 `len`，确保所有输入数据都被处理。
>    - 每次循环中，从 `input` 中取出四个连续的字节，通过位运算将其组合成一个无符号整数，并存储到 `output[i]` 中。
>      - `input[j]`：第一个字节，直接赋值。
>      - `input[j+1] << 8`：第二个字节，左移8位。
>      - `input[j+2] << 16`：第三个字节，左移16位。
>      - `input[j+3] << 24`：第四个字节，左移24位。
>    - 然后递增 `i` 和 `j`，继续处理下一组四个字节。
> 
> 3. **注意事项**：
>    - 该方法假设输入的 `len` 是4的倍数。如果不是，可能会导致未定义行为或访问越界错误。
>    - 在实际使用中，调用者需要确保 `output` 数组有足够的空间来存储解码后的结果，即 `output` 的大小应至少为 `len / 4`。
> 
> #### Example
> ```C++
> #include <stdio.h>
> 
> void MD5Decode(unsigned int *output, unsigned char *input, unsigned int len);
> 
> int main() {
>     unsigned char input[] = {0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0};
>     unsigned int output[2];
>     MD5Decode(output, input, 8);
> 
>     printf("Decoded result: %u, %u\n", output[0], output[1]);
>     return 0;
> }
> ```
> 
> 在这个例子中，`input` 包含8个字节的数据，`MD5Decode` 方法将其解码为两个无符号整数并存储在 `output` 数组中。
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)`.

The code of the Method is as follows:

```C++
void MD5Update(MD5_CTX *context,unsigned char *input,unsigned int inputlen)
{
	unsigned int i = 0,index = 0,partlen = 0;
	index = (context->count[0] >> 3) & 0x3F;
	partlen = 64 - index;
	context->count[0] += inputlen << 3;
	if(context->count[0] < (inputlen << 3)) {
		context->count[1]++;
	}
	context->count[1] += inputlen >> 29;

	if(inputlen >= partlen) {
		memcpy(&context->buffer[index],input,partlen);
		MD5Transform(context->state,context->buffer);
		for(i = partlen;i+64 <= inputlen;i+=64) {
			MD5Transform(context->state,&input[i]);
		}
		index = 0;
	} else {
		i = 0;
	}
	
	memcpy(&context->buffer[index],&input[i],inputlen-i);
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Transform(unsigned int [4] state, unsigned char [64] block)`

**Document**:

> ### void MD5Transform(unsigned int [4] state, unsigned char [64] block)
> #### Description
> 该方法用于执行MD5哈希算法的核心变换操作。它根据输入的64字节块更新状态数组`state`，这是MD5哈希计算过程中的关键步骤。
> 
> #### Parameters
> - `state`: 一个包含4个无符号整数的数组，表示当前的MD5哈希状态。
> - `block`: 一个包含64个字节的数组，表示待处理的数据块。
> 
> #### Code Details
> 详细分析如下：
> 
> 1. **初始化变量**：
>    ```C++
>    unsigned int a = state[0];
>    unsigned int b = state[1];
>    unsigned int c = state[2];
>    unsigned int d = state[3];
>    unsigned int x[64];
>    ```
>    这里将传入的状态数组`state`的四个元素分别赋值给局部变量`a`, `b`, `c`, `d`，以便后续使用。同时定义了一个大小为64的整型数组`x`，用于存储解码后的数据块。
> 
> 2. **解码输入数据块**：
>    ```C++
>    MD5Decode(x, block, 64);
>    ```
>    调用`MD5Decode`函数将输入的64字节数据块转换为16个无符号整数，并存储在数组`x`中。这一步是必要的，因为MD5算法需要以整数形式处理数据。
> 
> 3. **执行FF、GG、HH和II轮函数**：
>    ```C++
>    FF(a, b, c, d, x[ 0], 7, 0xd76aa478);
>    FF(d, a, b, c, x[ 1], 12, 0xe8c7b756);
>    ...
>    II(b, c, d, a, x[ 9], 21, 0xeb86d391);
>    ```
>    这些轮函数（FF、GG、HH、II）是MD5算法的核心部分，它们通过对`a`, `b`, `c`, `d`进行一系列复杂的位运算和加法操作来更新这些变量的值。每个轮函数接收多个参数，包括从解码后的数据块`x`中提取的值、旋转位移量以及常量值。具体来说：
>    - `FF`、`GG`、`HH`、`II`是不同的轮函数，每种函数有不同的操作逻辑。
>    - 每个轮函数调用时，会根据特定的索引从`x`中取出相应的值，并应用特定的旋转位移量和常量值。
>    - 这些轮函数的调用顺序和参数是严格按照MD5算法规范设计的。
> 
> 4. **更新状态数组**：
>    ```C++
>    state[0] += a;
>    state[1] += b;
>    state[2] += c;
>    state[3] += d;
>    ```
>    最后，将更新后的`a`, `b`, `c`, `d`的值累加到原始的状态数组`state`中，完成一次完整的MD5变换。
> 
> #### Example
> ```C++
> #include <stdio.h>
> 
> void MD5Transform(unsigned int state[4], unsigned char block[64]);
> 
> int main() {
>     unsigned int state[4] = {0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476};
>     unsigned char block[64] = { /* 填充64个字节的数据 */ };
>     
>     MD5Transform(state, block);
> 
>     printf("Updated state: %u, %u, %u, %u\n", state[0], state[1], state[2], state[3]);
>     return 0;
> }
> ```
> 在这个例子中，`state`数组初始化为MD5算法的标准初始值，`block`数组填充了64个字节的数据。调用`MD5Transform`方法后，`state`数组被更新，反映了对输入数据块的哈希变换结果。
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Encode(unsigned char * output, unsigned int * input, unsigned int len)`.

The code of the Method is as follows:

```C++
void MD5Encode(unsigned char *output,unsigned int *input,unsigned int len) {
	unsigned int i = 0,j = 0;
	while(j < len) {
		output[j] = input[i] & 0xFF;
		output[j+1] = (input[i] >> 8) & 0xFF;
		output[j+2] = (input[i] >> 16) & 0xFF;
		output[j+3] = (input[i] >> 24) & 0xFF;
		i++;
		j+=4;
	}
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. 
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Final(MD5_CTX * context, unsigned char [16] digest)`.

The code of the Method is as follows:

```C++
void MD5Final(MD5_CTX *context,unsigned char digest[16]) {
	unsigned int index = 0,padlen = 0;
	unsigned char bits[8];
	index = (context->count[0] >> 3) & 0x3F;
	padlen = (index < 56)?(56-index):(120-index);
	MD5Encode(bits,context->count,8);
	MD5Update(context,PADDING,padlen);
	MD5Update(context,bits,8);
	MD5Encode(digest,context->state,16);
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Encode(unsigned char * output, unsigned int * input, unsigned int len)`

**Document**:

> ### void MD5Encode(unsigned char * output, unsigned int * input, unsigned int len)
> #### Description
> 该函数用于将输入的无符号整数数组 `input` 编码为无符号字符数组 `output`，每个整数被拆分为四个字节。
> 
> #### Parameters
> - `output`: 指向输出缓冲区的指针，用于存储编码后的结果。类型为 `unsigned char *`。
> - `input`: 指向输入缓冲区的指针，包含需要编码的无符号整数数据。类型为 `unsigned int *`。
> - `len`: 输入数据的长度，以整数（`unsigned int`）为单位。类型为 `unsigned int`。
> 
> #### Code Details
> 该函数通过循环遍历输入数组 `input`，并将每个 `unsigned int` 类型的数据拆分为四个字节，依次存入输出数组 `output` 中。具体步骤如下：
> 
> 1. 初始化两个索引变量 `i` 和 `j`，分别用于遍历 `input` 和 `output` 数组。
> 2. 使用 `while` 循环遍历输入数组 `input`，直到处理完所有元素。
> 3. 在每次循环中：
>    - 将 `input[i]` 的最低字节（低 8 位）赋值给 `output[j]`。
>    - 将 `input[i]` 的第二个字节（第 9 到第 16 位）右移 8 位后赋值给 `output[j+1]`。
>    - 将 `input[i]` 的第三个字节（第 17 到第 24 位）右移 16 位后赋值给 `output[j+2]`。
>    - 将 `input[i]` 的最高字节（第 25 到第 32 位）右移 24 位后赋值给 `output[j+3]`。
> 4. 每次循环结束后，`i` 增加 1，`j` 增加 4，以便处理下一个 `unsigned int` 元素和对应的四个字节。
> 
> #### Example
> ```C++
> #include <stdio.h>
> 
> void MD5Encode(unsigned char *output, unsigned int *input, unsigned int len) {
>     unsigned int i = 0, j = 0;
>     while (j < len) {
>         output[j] = input[i] & 0xFF;
>         output[j+1] = (input[i] >> 8) & 0xFF;
>         output[j+2] = (input[i] >> 16) & 0xFF;
>         output[j+3] = (input[i] >> 24) & 0xFF;
>         i++;
>         j += 4;
>     }
> }
> 
> int main() {
>     unsigned int input[] = {0x12345678, 0x9ABCDEF0};
>     unsigned char output[8];
>     MD5Encode(output, input, 8);
> 
>     for (int i = 0; i < 8; i++) {
>         printf("%02X ", output[i]);
>     }
>     return 0;
> }
> ```
> 
> 上述示例代码展示了如何使用 `MD5Encode` 函数将一个包含两个 `unsigned int` 的数组转换为一个包含八个 `unsigned char` 的数组，并打印出转换后的结果。
---
**Method**: `void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)`

**Document**:

> ### void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)
> #### Description
> 该方法用于更新MD5上下文中的哈希状态，处理输入的数据块。它将输入数据分块处理，并调用`MD5Transform`方法进行核心变换。
> 
> #### Parameters
> - `context`: 指向`MD5_CTX`结构的指针，表示当前的MD5上下文。
> - `input`: 指向输入数据的指针，表示待处理的数据块。
> - `inputlen`: 无符号整数，表示输入数据的长度（以字节为单位）。
> 
> #### Code Details
> 详细分析如下：
> 
> 1. **初始化变量**：
>    ```C++
>    unsigned int i = 0, index = 0, partlen = 0;
>    ```
>    定义了三个局部变量：`i`用于循环计数，`index`用于记录当前缓冲区中的偏移量，`partlen`用于计算剩余空间。
> 
> 2. **计算当前缓冲区中的偏移量**：
>    ```C++
>    index = (context->count[0] >> 3) & 0x3F;
>    ```
>    计算当前缓冲区中已有的数据长度（以字节为单位），并将结果存储在`index`中。`context->count[0]`表示已处理的比特数，右移3位得到字节数，然后与`0x3F`（即63）进行按位与操作，确保`index`在0到63之间。
> 
> 3. **计算剩余空间**：
>    ```C++
>    partlen = 64 - index;
>    ```
>    计算当前缓冲区中剩余的空间大小，即64减去`index`。
> 
> 4. **更新已处理的比特数**：
>    ```C++
>    context->count[0] += inputlen << 3;
>    if(context->count[0] < (inputlen << 3)) {
>        context->count[1]++;
>    }
>    context->count[1] += inputlen >> 29;
>    ```
>    更新`context->count`数组，记录已处理的总比特数。首先将`inputlen`左移3位转换为比特数并累加到`context->count[0]`中。如果发生溢出，则增加`context->count[1]`。最后将`inputlen`右移29位，确保高位部分也被正确累加。
> 
> 5. **处理输入数据**：
>    ```C++
>    if(inputlen >= partlen) {
>        memcpy(&context->buffer[index], input, partlen);
>        MD5Transform(context->state, context->buffer);
>        for(i = partlen; i + 64 <= inputlen; i += 64) {
>            MD5Transform(context->state, &input[i]);
>        }
>        index = 0;
>    } else {
>        i = 0;
>    }
>    ```
>    如果输入数据长度大于或等于剩余空间`partlen`，则先将剩余空间填满并调用`MD5Transform`进行一次变换。然后继续处理后续的64字节块，直到所有完整的64字节块处理完毕。最后将`index`重置为0。如果输入数据长度小于`partlen`，则直接进入下一步。
> 
> 6. **复制剩余数据到缓冲区**：
>    ```C++
>    memcpy(&context->buffer[index], &input[i], inputlen - i);
>    ```
>    将剩余的数据复制到缓冲区中，等待下一次调用时继续处理。
> 
> #### Example
> ```C++
> #include <stdio.h>
> #include "md5.h"
> 
> int main() {
>     MD5_CTX context;
>     unsigned char input[] = "Hello, World!";
>     unsigned int inputlen = sizeof(input) - 1;
> 
>     MD5Init(&context);
>     MD5Update(&context, input, inputlen);
> 
>     printf("MD5 update completed.\n");
>     return 0;
> }
> ```
> 在这个例子中，`MD5_CTX`结构体被初始化后，通过`MD5Update`方法更新哈希状态，处理输入字符串`"Hello, World!"`。
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Init(MD5_CTX * context)`.

The code of the Method is as follows:

```C++
void MD5Init(MD5_CTX *context) {
	context->count[0] = 0;
	context->count[1] = 0;
	context->state[0] = 0x67452301;
	context->state[1] = 0xEFCDAB89;
	context->state[2] = 0x98BADCFE;
	context->state[3] = 0x10325476;
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. 
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is main.c.
Now you need to generate a document for a Method, whose name is `int main(int argc, char *[] argv)`.

The code of the Method is as follows:

```C++
int main(int argc, char *argv[]) {
	int i, n;
	bool isfile = false;
	unsigned char decrypt[16];
	MD5_CTX md5;
	
	if(argc > 1 && strlen(argv[1]) == 2 && !memcmp(argv[1], "-f", 2)) {
		isfile = true;
	}
	
	if(argc == 1 || (argc == 2 && isfile)) {
		fprintf(stderr, "usage:\n    %s -f file ...\n    %s string ...\n", argv[0], argv[0]);
		return 1;
	}
	
	if(isfile) {
		FILE *fp;
		for(n=2; n<argc; n++) {
			fp = fopen(argv[n], "rb");
			if(fp == NULL) {
				fprintf(stderr, "File %s not exists, errno = %d, error = %s\n", argv[n], errno, strerror(errno));
				continue;
			}
			
			MD5Init(&md5);
			
			do {
				unsigned char encrypt[1024];
				while(!feof(fp)) {
					MD5Update(&md5, encrypt, fread(encrypt, 1, sizeof(encrypt), fp));
				}
				fclose(fp);
			} while(0);
			
			MD5Final(&md5, decrypt);

			for(i=0; i<16; i++) {
				printf("%02x", decrypt[i]);  //02x前需要加上 %
			}
			
			printf("  %s\n", argv[n]);
		}
	} else {
		for(n=1; n<argc; n++) {
			MD5Init(&md5);
			MD5Update(&md5, argv[n], strlen(argv[n]));
			MD5Final(&md5, decrypt);

			for(i=0; i<16; i++) {
				printf("%02x", decrypt[i]);  //02x前需要加上 %
			}
			
			printf("  %s\n", argv[n]);
		}
	}

	return 0;
}
```


Also, the code has been called by the following methods, their code and docs are as following:
**Method**: `void MD5Init(MD5_CTX * context)`

**Document**:

> ### void MD5Init(MD5_CTX * context)
> #### Description
> 初始化 MD5 上下文对象，设置初始状态和计数器。
> 
> #### Parameters
> - `context`: 指向 MD5_CTX 结构的指针，用于存储 MD5 算法的状态和处理的数据长度。
> 
> #### Code Details
> `MD5Init` 方法用于初始化一个 MD5 上下文对象 `context`。具体来说，它执行以下操作：
> 
> 1. 将 `context->count[0]` 和 `context->count[1]` 设置为 0。这两个变量用于记录已处理的数据长度（以位为单位），其中 `count[0]` 存储低 32 位，`count[1]` 存储高 32 位。
> 2. 初始化 `context->state` 数组中的四个元素为特定的初始值：
>    - `context->state[0]` 被设置为 `0x67452301`
>    - `context->state[1]` 被设置为 `0xEFCDAB89`
>    - `context->state[2]` 被设置为 `0x98BADCFE`
>    - `context->state[3]` 被设置为 `0x10325476`
> 
> 这些初始值是 MD5 算法中规定的标准初始值，用于确保算法的一致性和正确性。
> 
> #### Example
> ```C++
> #include "md5.h"
> 
> int main() {
>     MD5_CTX context;
>     MD5Init(&context);
>     // 继续使用初始化后的 context 进行其他 MD5 操作
>     return 0;
> }
> ```
---
**Method**: `void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)`

**Document**:

> ### void MD5Update(MD5_CTX * context, unsigned char * input, unsigned int inputlen)
> #### Description
> 该方法用于更新MD5上下文中的哈希状态，处理输入的数据块。它将输入数据分块处理，并调用`MD5Transform`方法进行核心变换。
> 
> #### Parameters
> - `context`: 指向`MD5_CTX`结构的指针，表示当前的MD5上下文。
> - `input`: 指向输入数据的指针，表示待处理的数据块。
> - `inputlen`: 无符号整数，表示输入数据的长度（以字节为单位）。
> 
> #### Code Details
> 详细分析如下：
> 
> 1. **初始化变量**：
>    ```C++
>    unsigned int i = 0, index = 0, partlen = 0;
>    ```
>    定义了三个局部变量：`i`用于循环计数，`index`用于记录当前缓冲区中的偏移量，`partlen`用于计算剩余空间。
> 
> 2. **计算当前缓冲区中的偏移量**：
>    ```C++
>    index = (context->count[0] >> 3) & 0x3F;
>    ```
>    计算当前缓冲区中已有的数据长度（以字节为单位），并将结果存储在`index`中。`context->count[0]`表示已处理的比特数，右移3位得到字节数，然后与`0x3F`（即63）进行按位与操作，确保`index`在0到63之间。
> 
> 3. **计算剩余空间**：
>    ```C++
>    partlen = 64 - index;
>    ```
>    计算当前缓冲区中剩余的空间大小，即64减去`index`。
> 
> 4. **更新已处理的比特数**：
>    ```C++
>    context->count[0] += inputlen << 3;
>    if(context->count[0] < (inputlen << 3)) {
>        context->count[1]++;
>    }
>    context->count[1] += inputlen >> 29;
>    ```
>    更新`context->count`数组，记录已处理的总比特数。首先将`inputlen`左移3位转换为比特数并累加到`context->count[0]`中。如果发生溢出，则增加`context->count[1]`。最后将`inputlen`右移29位，确保高位部分也被正确累加。
> 
> 5. **处理输入数据**：
>    ```C++
>    if(inputlen >= partlen) {
>        memcpy(&context->buffer[index], input, partlen);
>        MD5Transform(context->state, context->buffer);
>        for(i = partlen; i + 64 <= inputlen; i += 64) {
>            MD5Transform(context->state, &input[i]);
>        }
>        index = 0;
>    } else {
>        i = 0;
>    }
>    ```
>    如果输入数据长度大于或等于剩余空间`partlen`，则先将剩余空间填满并调用`MD5Transform`进行一次变换。然后继续处理后续的64字节块，直到所有完整的64字节块处理完毕。最后将`index`重置为0。如果输入数据长度小于`partlen`，则直接进入下一步。
> 
> 6. **复制剩余数据到缓冲区**：
>    ```C++
>    memcpy(&context->buffer[index], &input[i], inputlen - i);
>    ```
>    将剩余的数据复制到缓冲区中，等待下一次调用时继续处理。
> 
> #### Example
> ```C++
> #include <stdio.h>
> #include "md5.h"
> 
> int main() {
>     MD5_CTX context;
>     unsigned char input[] = "Hello, World!";
>     unsigned int inputlen = sizeof(input) - 1;
> 
>     MD5Init(&context);
>     MD5Update(&context, input, inputlen);
> 
>     printf("MD5 update completed.\n");
>     return 0;
> }
> ```
> 在这个例子中，`MD5_CTX`结构体被初始化后，通过`MD5Update`方法更新哈希状态，处理输入字符串`"Hello, World!"`。
---
**Method**: `void MD5Final(MD5_CTX * context, unsigned char [16] digest)`

**Document**:

> ### void MD5Final(MD5_CTX * context, unsigned char [16] digest)
> #### Description
> 该方法用于完成MD5哈希计算的最终处理步骤，将当前的MD5上下文转换为16字节的摘要。
> 
> #### Parameters
> - `context`: 指向`MD5_CTX`结构的指针，表示当前的MD5上下文。
> - `digest`: 指向输出缓冲区的指针，用于存储生成的16字节MD5摘要。类型为`unsigned char [16]`。
> 
> #### Code Details
> 详细分析如下：
> 
> 1. **初始化变量**：
>    ```C++
>    unsigned int index = 0, padlen = 0;
>    unsigned char bits[8];
>    ```
>    定义了两个局部变量：`index`用于记录当前缓冲区中的偏移量，`padlen`用于计算填充长度。`bits`数组用于存储输入数据的比特数（以字节形式）。
> 
> 2. **计算当前缓冲区中的偏移量**：
>    ```C++
>    index = (context->count[0] >> 3) & 0x3F;
>    ```
>    计算当前缓冲区中已有的数据长度（以字节为单位），并将结果存储在`index`中。`context->count[0]`表示已处理的比特数，右移3位得到字节数，然后与`0x3F`（即63）进行按位与操作，确保`index`在0到63之间。
> 
> 3. **计算填充长度**：
>    ```C++
>    padlen = (index < 56) ? (56 - index) : (120 - index);
>    ```
>    根据当前缓冲区中的偏移量`index`，计算需要填充的字节数`padlen`。如果`index`小于56，则填充到56；否则填充到120（即下一个64字节块的起始位置减去8个字节的比特数）。
> 
> 4. **编码比特数**：
>    ```C++
>    MD5Encode(bits, context->count, 8);
>    ```
>    调用`MD5Encode`函数将`context->count`中的比特数编码为8字节的字符数组`bits`。
> 
> 5. **更新MD5上下文**：
>    ```C++
>    MD5Update(context, PADDING, padlen);
>    MD5Update(context, bits, 8);
>    ```
>    分别调用`MD5Update`函数两次，首先将填充数据`PADDING`和填充长度`padlen`更新到MD5上下文中，然后将比特数`bits`更新到MD5上下文中。
> 
> 6. **生成最终摘要**：
>    ```C++
>    MD5Encode(digest, context->state, 16);
>    ```
>    最后调用`MD5Encode`函数将`context->state`中的状态值编码为16字节的字符数组`digest`，作为最终的MD5摘要。
> 
> #### Example
> ```C++
> #include <stdio.h>
> #include "md5.h"
> 
> int main() {
>     MD5_CTX context;
>     unsigned char digest[16];
> 
>     MD5Init(&context);
>     MD5Update(&context, (unsigned char *)"Hello, World!", 13);
>     MD5Final(&context, digest);
> 
>     for (int i = 0; i < 16; i++) {
>         printf("%02X", digest[i]);
>     }
>     printf("\n");
> 
>     return 0;
> }
> ```
> 在这个例子中，`MD5_CTX`结构体被初始化后，通过`MD5Update`方法更新哈希状态，处理输入字符串`"Hello, World!"`，最后调用`MD5Final`方法生成并打印16字节的MD5摘要。
---


Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. And please include the reference relationship with its callers or callees in the project from a functional perspective
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. You can refer to the use of this Function in the caller.
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`.

The code of the Method is as follows:

```C++
void MD5Decode(unsigned int *output,unsigned char *input,unsigned int len) {
	unsigned int i = 0,j = 0;
	while(j < len) {
		output[i] = (input[j]) | (input[j+1] << 8) | (input[j+2] << 16) | (input[j+3] << 24);
		i++;
		j+=4;
	}
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. 
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`.

The code of the Method is as follows:

```C++
void MD5Decode(unsigned int *output,unsigned char *input,unsigned int len) {
	unsigned int i = 0,j = 0;
	while(j < len) {
		output[i] = (input[j]) | (input[j+1] << 8) | (input[j+2] << 16) | (input[j+3] << 24);
		i++;
		j+=4;
	}
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. 
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.

Currently, you are in a project and the related hierarchical structure of this project is as follows
md5
  main.c
  md5.c
  md5.h

The path of the document you need to generate in this project is md5.c.
Now you need to generate a document for a Method, whose name is `void MD5Decode(unsigned int * output, unsigned char * input, unsigned int len)`.

The code of the Method is as follows:

```C++
void MD5Decode(unsigned int *output,unsigned char *input,unsigned int len) {
	unsigned int i = 0,j = 0;
	while(j < len) {
		output[i] = (input[j]) | (input[j+1] << 8) | (input[j+2] << 16) | (input[j+3] << 24);
		i++;
		j+=4;
	}
}
```




Please generate a detailed explanation document for this Method based on the code of the target Method itself and combine it with its calling situation in the project.

Please write out the function of this Method briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Method in one sentence.
> #### Parameters
> - Parameter1: XXX
> - Parameter2: XXX
> - ...
> #### Code Details
> Detailed and CERTAIN code analysis of the Method. 
> #### Example
> ```C++
> Mock possible usage examples of the Method with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation for the target object in a professional way.
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.

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

Note:
- Never output anything except the directory structure.

You should output as follows:

my_cpp_project         
  include
    my_cpp_project
    my_class.h
  src
    main.cpp
    my_class.cpp

md5
  main.c
  md5.c
  md5.h
You must output in Chinese though the prompt is written in English.You can write with some English words in the analysis and description to enhance the document's readability because you do not need to translate the function name or variable name into the target language.
