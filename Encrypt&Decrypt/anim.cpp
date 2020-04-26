

int sub_45E720(void *this, void **data_buff, int data_length, int decoded_data, unsigned int a5, unsigned int *this_father)
{
  int v7; // [esp+Ch] [ebp-24h]
  unsigned int i; // [esp+14h] [ebp-1Ch]
  unsigned int j; // [esp+14h] [ebp-1Ch]
  char v10[16]; // [esp+18h] [ebp-18h]
  void *_data_buff; // [esp+2Ch] [ebp-4h]

  if ( !data_buff || !decoded_data || !this_father )
    return 3;
  *this_father = (*(int (__thiscall **)(void *, int))(*(int *)this + 16))(this, data_length);// ret length-0x14
  if ( *this_father > a5 )
    return 11;
  _data_buff = *data_buff;
  if ( *_data_buff != 1000000 )
    return 10;
  for ( i = 0; i < 0x10; ++i )
    v10[i] = *((char *)data_buff + i + 4);
  v7 = 0;
  for ( j = 0; j < *this_father; ++j )
  {
    *(char *)(j + decoded_data) = (v10[v7] | *((char *)data_buff + j + 20)) & ~(v10[v7] & *((char *)data_buff + j + 20));
    if ( ++v7 == 16 )
    {
      v7 = 0;
      sub_45E1A0(v10, *(char *)(j + decoded_data - 1));
    }
  }
  return 0;
}

char * sub_45E1A0(char *key, char ch)
{
  char *result; // eax

  switch ( ch & 7 )
  {
    case 0:
      *key += ch;
      key[3] += ch + 2;
      key[4] = key[2] + ch + 11;
      result = key;
      key[8] = key[6] + 7;
      break;
    case 1:
      key[2] = key[9] + key[10];
      key[6] = key[7] + key[15];
      key[8] += key[1];
      result = key;
      key[15] = key[5] + key[3];
      break;
    case 2:
      key[1] += key[2];
      key[5] += key[6];
      key[7] += key[8];
      result = key;
      key[10] += key[11];
      break;
    case 3:
      key[9] = key[2] + key[1];
      key[11] = key[6] + key[5];
      key[12] = key[8] + key[7];
      result = key;
      key[13] = key[11] + key[10];
      break;
    case 4:
      *key = key[1] + 111;
      key[3] = key[4] + 71;
      key[4] = key[5] + 17;
      result = key;
      key[14] = key[15] + 64;
      break;
    case 5:
      key[2] += key[10];
      key[4] = key[5] + key[12];
      key[6] = key[8] + key[14];
      result = key;
      key[8] = key[11] + *key;
      break;
    case 6:
      key[9] = key[11] + key[1];
      key[11] = key[13] + key[3];
      key[13] = key[15] + key[5];
      key[15] = key[9] + key[7];
      goto LABEL_9;
    default:
LABEL_9:
      key[1] = key[9] + key[5];
      key[2] = key[10] + key[6];
      key[3] = key[11] + key[7];
      result = key;
      key[4] = key[12] + key[8];
      break;
  }
  return result;
}


int main()
{
    return 0;
}