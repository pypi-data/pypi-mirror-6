
#include <stdio.h>
#include <stddef.h>
#include <stdarg.h>
#include <errno.h>
#include <sys/types.h>   /* XXX for ssize_t on some platforms */

#ifdef _WIN32
#  include <Windows.h>
#  define snprintf _snprintf
typedef __int8 int8_t;
typedef __int16 int16_t;
typedef __int32 int32_t;
typedef __int64 int64_t;
typedef unsigned __int8 uint8_t;
typedef unsigned __int16 uint16_t;
typedef unsigned __int32 uint32_t;
typedef unsigned __int64 uint64_t;
typedef SSIZE_T ssize_t;
typedef unsigned char _Bool;
#else
#  include <stdint.h>
#endif


    #include "hiredis.h"
    
void _cffi_f_freeReplyObject(void * x0)
{
  freeReplyObject(x0);
}

struct redisReader * _cffi_f_redisReaderCreate(void)
{
  return redisReaderCreate();
}

int _cffi_f_redisReaderFeed(struct redisReader * x0, char const * x1, size_t x2)
{
  return redisReaderFeed(x0, x1, x2);
}

void _cffi_f_redisReaderFree(struct redisReader * x0)
{
  redisReaderFree(x0);
}

int _cffi_f_redisReaderGetReply(struct redisReader * x0, redisReply * * x1)
{
  return redisReaderGetReply(x0, x1);
}

static void _cffi_check_struct_redisReader(struct redisReader *p)
{
  /* only to generate compile-time warnings or errors */
}
ssize_t _cffi_layout_struct_redisReader(ssize_t i)
{
  struct _cffi_aligncheck { char x; struct redisReader y; };
  static ssize_t nums[] = {
    sizeof(struct redisReader),
    offsetof(struct _cffi_aligncheck, y),
    -1
  };
  return nums[i];
  /* the next line is not executed, but compiled */
  _cffi_check_struct_redisReader(0);
}

static void _cffi_check_struct_redisReply(struct redisReply *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->type) << 1);
  (void)((p->integer) << 1);
  (void)((p->len) << 1);
  { char * *tmp = &p->str; (void)tmp; }
  (void)((p->elements) << 1);
  { redisReply * * *tmp = &p->element; (void)tmp; }
}
ssize_t _cffi_layout_struct_redisReply(ssize_t i)
{
  struct _cffi_aligncheck { char x; struct redisReply y; };
  static ssize_t nums[] = {
    sizeof(struct redisReply),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct redisReply, type),
    sizeof(((struct redisReply *)0)->type),
    offsetof(struct redisReply, integer),
    sizeof(((struct redisReply *)0)->integer),
    offsetof(struct redisReply, len),
    sizeof(((struct redisReply *)0)->len),
    offsetof(struct redisReply, str),
    sizeof(((struct redisReply *)0)->str),
    offsetof(struct redisReply, elements),
    sizeof(((struct redisReply *)0)->elements),
    offsetof(struct redisReply, element),
    sizeof(((struct redisReply *)0)->element),
    -1
  };
  return nums[i];
  /* the next line is not executed, but compiled */
  _cffi_check_struct_redisReply(0);
}

