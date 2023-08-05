# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

INCLUDES = """
#include <openssl/err.h>
"""

TYPES = """
struct ERR_string_data_st {
    unsigned long error;
    const char *string;
};
typedef struct ERR_string_data_st ERR_STRING_DATA;

static const int ERR_LIB_EVP;
static const int ERR_LIB_PEM;

static const int EVP_F_EVP_ENCRYPTFINAL_EX;
static const int EVP_F_EVP_DECRYPTFINAL_EX;

static const int EVP_R_DATA_NOT_MULTIPLE_OF_BLOCK_LENGTH;

static const int PEM_F_PEM_READ_BIO_PRIVATEKEY;
static const int PEM_F_D2I_PKCS8PRIVATEKEY_BIO;

static const int PEM_R_BAD_PASSWORD_READ;
static const int ASN1_R_BAD_PASSWORD_READ;
"""

FUNCTIONS = """
void ERR_load_crypto_strings(void);
void ERR_free_strings(void);
char* ERR_error_string(unsigned long, char *);
void ERR_error_string_n(unsigned long, char *, size_t);
const char* ERR_lib_error_string(unsigned long);
const char* ERR_func_error_string(unsigned long);
const char* ERR_reason_error_string(unsigned long);
void ERR_print_errors(BIO *);
void ERR_print_errors_fp(FILE *);
unsigned long ERR_get_error(void);
unsigned long ERR_peek_error(void);
unsigned long ERR_peek_last_error(void);
unsigned long ERR_get_error_line(const char **, int *);
unsigned long ERR_peek_error_line(const char **, int *);
unsigned long ERR_peek_last_error_line(const char **, int *);
unsigned long ERR_get_error_line_data(const char **, int *,
                                      const char **, int *);
unsigned long ERR_peek_error_line_data(const char **,
                                       int *, const char **, int *);
unsigned long ERR_peek_last_error_line_data(const char **,
                                            int *, const char **, int *);
void ERR_put_error(int, int, int, const char *, int);
void ERR_add_error_data(int, ...);
int ERR_get_next_error_library(void);
"""

MACROS = """
unsigned long ERR_PACK(int, int, int);
int ERR_GET_LIB(unsigned long);
int ERR_GET_FUNC(unsigned long);
int ERR_GET_REASON(unsigned long);
int ERR_FATAL_ERROR(unsigned long);
"""

CUSTOMIZATIONS = """
"""

CONDITIONAL_NAMES = {}
