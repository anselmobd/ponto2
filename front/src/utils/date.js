import moment from 'moment';

export function dateTime2Text(date_time) {
  const date = date_time.toLocaleDateString(
    'pt-br',
    {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit'
    }
  );
  const time = date_time.toLocaleTimeString('pt-br');
  return date + ' ' + time;
}

export function date2Text(data) {
  return moment.utc(data).format('DD/MM/YY');
}

export function date2InputText(date) {  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function inputStrDate2PtBrDate(str_date, empty='') {
  if (str_date) {
    return (new Date(str_date)).toLocaleDateString('pt-BR', { timeZone: 'UTC' });
  } else {
    return empty;
  }
}

