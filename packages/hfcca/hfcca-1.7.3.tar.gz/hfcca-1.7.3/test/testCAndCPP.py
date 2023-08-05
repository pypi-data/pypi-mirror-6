import unittest
from lizard import  analyze_file, CLikeReader

def get_cpp_fileinfo(source_code):
    return analyze_file.analyze_source_code_with_parser("", source_code, CLikeReader())

def get_cpp_function_list(source_code):
    return get_cpp_fileinfo(source_code).function_list

class Test_C_Token_extension(unittest.TestCase):

    def test_include_brackets(self):
        extended = CLikeReader().extend_tokens((("#include", 1), ("<",1), ("aa.h", 1), (">", 1)))
        self.assertEqual(("<aa.h>", 1), list(extended)[1])

    def test_include_brackets_with_quotes(self):
        extended = CLikeReader().extend_tokens((("#include", 1), ('"aa.h"', 1)))
        self.assertEqual(('"aa.h"', 1), list(extended)[1])

class Test_C_Token_Count(unittest.TestCase):

    def test_non_function_tokens_are_counted(self):
        fileinfo = get_cpp_fileinfo("int i, j;")
        self.assertEqual(5, fileinfo.token_count)

    def test_include_is_counted_as_2(self):
        fileinfo = get_cpp_fileinfo("#include \"abc.h\"")
        self.assertEqual(2, fileinfo.token_count)

    def test_include_with_lg_and_gg_is_counted_as_2(self):
        fileinfo = get_cpp_fileinfo("#include <abc.h>")
        self.assertEqual(2, fileinfo.token_count)

    def test_one_function_with_no_token(self):
        result = get_cpp_function_list("int fun(){}")
        self.assertEqual(5, result[0].token_count)

    def test_one_function_with_one_token(self):
        result = get_cpp_function_list("int fun(){;}")
        self.assertEqual(6, result[0].token_count)

    def test_one_function_with_content(self):
        result = get_cpp_function_list("int fun(){if(a){xx;}}")
        self.assertEqual(13, result[0].token_count)

    def test_one_function_with_comments_only(self):
        result = get_cpp_function_list("int fun(){/**/}")
        self.assertEqual(5, result[0].token_count)
        
class Test_c_cpp_lizard(unittest.TestCase):
    def test_empty(self):
        result = get_cpp_function_list("")
        self.assertEqual(0, len(result))
        
    def test_no_function(self):
        result = get_cpp_function_list("#include <stdio.h>\n")
        self.assertEqual(0, len(result))
    
    def test_one_function(self):
        result = get_cpp_function_list("int fun(){}")
        self.assertEqual(1, len(result))
        self.assertEqual("fun", result[0].name)
        self.assertEqual(1, result[0].cyclomatic_complexity)
    
    def test_two_function(self):
        result = get_cpp_function_list("int fun(){}\nint fun1(){}\n")
        self.assertEqual(2, len(result))
        self.assertEqual("fun", result[0].name)
        self.assertEqual("fun1", result[1].name)
        self.assertEqual(1, result[0].start_line)
        self.assertEqual(1, result[0].end_line)
        self.assertEqual(2, result[1].start_line)
        self.assertEqual(2, result[1].end_line)
    
    def test_function_with_content(self):
        result = get_cpp_function_list("int fun(xx oo){int a; a= call(p1,p2);}")
        self.assertEqual(1, len(result))
        self.assertEqual("fun", result[0].name)
        self.assertEqual(1, result[0].cyclomatic_complexity)
        self.assertEqual("fun( xx oo )", result[0].long_name)
    
    def test_one_function_with_content(self):
        result = get_cpp_function_list("int fun(){if(a){xx;}}")
        self.assertEqual(2, result[0].cyclomatic_complexity)
        self.assertEqual(1, result[0].nloc)

    def test_nloc_of_empty_function(self):
        result = get_cpp_function_list("int fun(){}")
        self.assertEqual(1, result[0].nloc)
    
    def test_nloc(self):
        result = get_cpp_function_list("int fun(){\n\n\n}")
        self.assertEqual(2, result[0].nloc)
    
    def test_nloc2(self):
        result = get_cpp_function_list("int fun(){aa();\n\n\n\nbb();\n\n\n}")
        self.assertEqual(3, result[0].nloc)
        self.assertEqual(1, result[0].start_line)
        self.assertEqual(8, result[0].end_line)
    
    def test_one_function_with_question_mark(self):
        result = get_cpp_function_list("int fun(){return (a)?b:c;}")
        self.assertEqual(2, result[0].cyclomatic_complexity)
    
    def test_one_function_with_forever_loop(self):
        result = get_cpp_function_list("int fun(){for(;;){dosomething();}}")
        self.assertEqual(1, len(result))
        self.assertEqual(2, result[0].cyclomatic_complexity)
    
    def test_one_function_with_and(self):
        result = get_cpp_function_list("int fun(){if(a&&b){xx;}}")
        self.assertEqual(3, result[0].cyclomatic_complexity)
    
    def test_one_function_with_else_if(self):
        result = get_cpp_function_list("int fun(){if(a)b;else if (c) d;}")
        self.assertEqual(3, result[0].cyclomatic_complexity)
    
    def test_double_slash_within_string(self):
        result = get_cpp_function_list("""int fun(){char *a="\\\\";}""")
        self.assertEqual(1, result[0].cyclomatic_complexity)
    
    def test_function_with_no_param(self):
        result = get_cpp_function_list("int fun(){}")
        self.assertEqual(0, result[0].parameter_count)
    
    def test_function_with_1_param(self):
        result = get_cpp_function_list("int fun(aa * bb){}")
        self.assertEqual(1, result[0].parameter_count)
    
    def test_function_with_param(self):
        result = get_cpp_function_list("int fun(aa * bb, cc dd){}")
        self.assertEqual(2, result[0].parameter_count)
    
    def test_function_with_strang_param(self):
        result = get_cpp_function_list("int fun(aa<mm, nn> bb){}")
        self.assertEqual(1, result[0].parameter_count)
    
    def test_one_function1(self):
        result = get_cpp_function_list("int abc::fun(){}")
        self.assertEqual(1, len(result))
        self.assertEqual("abc::fun", result[0].name)
        self.assertEqual("abc::fun( )", result[0].long_name)
        self.assertEqual(1, result[0].cyclomatic_complexity)
    
    def test_one_function_with_const(self):
        result = get_cpp_function_list("int abc::fun()const{}")
        self.assertEqual(1, len(result))
        self.assertEqual("abc::fun", result[0].name)
        self.assertEqual("abc::fun( ) const", result[0].long_name)
        self.assertEqual(1, result[0].cyclomatic_complexity)

    def test_one_function_in_class(self):
        result = get_cpp_function_list("class c {~c(){}}; int d(){}")
        self.assertEqual(2, len(result))
        self.assertEqual("c", result[0].name)
        self.assertEqual("d", result[1].name)
        
    def test_template_as_reference(self):
        result = get_cpp_function_list("abc::def(a<b>& c){}")
        self.assertEqual(1, len(result))

    def test_template_with_pointer(self):
        result = get_cpp_function_list("abc::def(a<b*> c){}")
        self.assertEqual(1, len(result))
        
    def test_template_with_reference(self):
        result = get_cpp_function_list("void fun(t<int &>b){} ")
        self.assertEqual(1, len(result))
        
    def test_template_with_reference_as_reference(self):
        result = get_cpp_function_list("void fun(t<const int&>&b){} ")
        self.assertEqual(1, len(result))
       
    def test_operator_overloading(self):
        result = get_cpp_function_list("bool operator +=(int b){}")
        self.assertEqual(1, len(result))
        self.assertEqual("operator +=", result[0].name)
                
    def test_operator_overloading_with_namespace(self):
        result = get_cpp_function_list("bool TC::operator !(int b){}")
        self.assertEqual(1, len(result))
        self.assertEqual("TC::operator !", result[0].name)
                
    def test_function_operator(self):
        result = get_cpp_function_list("bool TC::operator ()(int b){}")
        self.assertEqual(1, len(result))
        self.assertEqual("TC::operator ( )", result[0].name)

    def test_constructor_initialization_list(self):
        result = get_cpp_function_list('''A::A():a(1){}''')
        self.assertEqual(1, len(result))
        self.assertEqual("A::A", result[0].name)
        
    def test_brakets_before_function(self):
        result = get_cpp_function_list('''()''')
        self.assertEqual(0, len(result))
        

class Test_Preprocessing(unittest.TestCase):

    def test_braces_in_harsh_else(self):
        result = get_cpp_function_list('''int main(){
                                        #ifndef NORBUS
                                        {
                                        #else
                                        {
                                        #endif
                                        }
                                    } void fun(){}''')
        self.assertEqual(2, len(result))

    def test_content_macro_should_be_ignored(self):
        result = get_cpp_function_list(r'''
                    #define MTP_CHEC                    \
                       int foo () {                     \
                        }
               ''')
        self.assertEqual(0, len(result))
    
   
    def test_preprocessors_should_be_ignored_outside_function_implementation(self):
        result = get_cpp_function_list('''
                      Constructor::Constructor()
                      #ifdef MAGIC
                      :m_timer(5)
                      #endif
                      {}
                    ''')
        self.assertEqual(1, len(result))

    def test_sharp_if_and_sharp_elif_counts_in_cc_number(self):
        result = get_cpp_function_list('''
                int main(){
                #ifdef A
                #elif (defined E)
                #endif
                }''')
        self.assertEqual(1, len(result))
        self.assertEqual(3, result[0].cyclomatic_complexity)

    def test_preprocessor_is_not_function(self):
        result = get_cpp_function_list('''
                #ifdef A
                #elif (defined E)
                #endif
                ''')
        self.assertEqual(0, len(result))

