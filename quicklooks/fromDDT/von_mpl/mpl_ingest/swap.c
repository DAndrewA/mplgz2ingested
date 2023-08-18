/* functions to swap bytes within short int and long int arrays */
/* t.j. martin 2/18/93 */

/* compile with "cc -c swap.c"  produces swap.o for later linking */

void swap2(buf,num)
char *buf; int num;
{
	int i;
	char b0, b1;
	for(i=0; i<num; i++)
	{
		b0 = *(buf);
		b1 = *(buf+1);
		*buf++ = b1;
		*buf++ = b0;
	}
}
void swap4(buf,num)
char *buf; int num;
{
	int i;
	char b0, b1, b2, b3;
	for(i=0; i<num; i++)
	{
		b0 = *(buf);
		b1 = *(buf+1);
		b2 = *(buf+2);
		b3 = *(buf+3);
		*buf++ = b3;
		*buf++ = b2;
		*buf++ = b1;
		*buf++ = b0;
	}
}
void swap8(buf,num)
char *buf; int num;
{
	int i;
	char b0, b1, b2, b3, b4, b5, b6, b7;
	for(i=0; i<num; i++)
	{
		b0 = *(buf);
		b1 = *(buf+1);
		b2 = *(buf+2);
		b3 = *(buf+3);
		b4 = *(buf+4);
		b5 = *(buf+5);
		b6 = *(buf+6);
		b7 = *(buf+7);
		*buf++ = b7;
		*buf++ = b6;
		*buf++ = b5;
		*buf++ = b4;
		*buf++ = b3;
		*buf++ = b2;
		*buf++ = b1;
		*buf++ = b0;
	}
}

