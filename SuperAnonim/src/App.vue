<script setup>
import {ref, computed, onMounted} from "vue";
import axios from "axios";
import {Notifications, notify} from "@kyvg/vue3-notification";


onMounted(() => {
  notify({text: 'Пользуясь сайтом вы соглашаетесь с <a href="http://localhost:8080/sogl">пользовательским соглашением</a>'})
})


const lol = ref({
  href: '',
  download: ''
});

const off = ref(true);

const down = ref(false);

const butText = ref('Выберите файл')

const chek = ref([
  {
    title: 'Серия и номер паспорта',
    disabled: false,
    name: 'passport'
  },
  {
    title: 'Номер телефона',
    disabled: false,
    name: 'phone'
  },
  {
    title: 'Полис ОМС',
    disabled: false,
    name: 'oms'
  },
  {
    title: 'СНИЛС',
    disabled: false,
    name: 'snils'
  },
  {
    title: 'Почта',
    disabled: false,
    name: 'email'
  },
  {
    title: 'ФИО',
    disabled: false,
    name: 'fio'
  },
  {
    title: 'ИНН',
    disabled: false,
    name: 'inn'
  },
]);

const data = ref({
  'inn': false,
  'fio': false,
  'email': false,
  'snils': false,
  'oms': false,
  'phone': false,
  'passport': false,
  'pdf': false
});

const dis = computed(() => {
  let flag = 0;
  Object.keys(data.value).forEach((elem) => data.value[elem] ? flag++ : flag)
  return !!!flag
})

const handler = (event) => {
  const files = event.target.files[0];
  const formData = new FormData();
  down.value = false;
  data.value.pdf = false;
  butText.value = files.name;
  if (files.name.toLowerCase().slice(-4) !== '.png' &&
    files.name.toLowerCase().slice(-5) !== '.jpeg' &&
    files.name.toLowerCase().slice(-4) !== '.img' &&
    files.name.toLowerCase().slice(-4) !== '.jpg' &&
    files.name.toLowerCase().slice(-4) !== '.pdf') {
    notify({
      text: 'Формат файла не поддерживается',
      type: 'negative'
    })
    return 0;
  }
  if (files.name.toLowerCase().slice(-4) === '.pdf') {
    data.value.pdf = true;
  }
  formData.append('file', files);
  formData.append('documentJson', JSON.stringify(data.value));
  axios.post('http://localhost:8080/', formData)
    .then((res) => {
      if (files.name.toLowerCase().slice(-4) === '.pdf') {
        lol.value.href = "data:application/pdf;base64," + res.data
        lol.value.download = 'anonpdf.pdf'
      } else {
        lol.value.download = 'anonimg.png'
        lol.value.href = "data:image/png;base64," + res.data;
      }
      down.value = true;
    })
    .catch((err) => {
      notify({
        text: 'Ошибка: ' + err,
        duration: 5000,
        type: 'negative',
      });
      event.target.value = '';
      butText.value = 'Выберите файл';
      }
    );

  return 0;
}
</script>

<template>
  <main>
    <div class="box">
      <div class="title">
        Super<span style="color: #1d3557">Anonim</span>
      </div>
      <div class="page">
        <div class="cont1">
        <span style="color: #E63946; font-weight: 600; font-size: 32px">
          Что вы хотите скрыть?
        </span>
          <div class="form">
            <label v-for="elem in chek" style="font-weight: 600"
                   :style="{color: elem.disabled ? '#4a5d79' : '#1d3557'}">
              <input :disabled="elem.disabled || off" type="checkbox" :name="elem.name"
                     v-model="data[elem.name]"/>
              {{ elem.title }}
            </label>
          </div>
        </div>
        <div class="cont3">
          <div class="cont2">
          <span style="font-weight: 600; font-size: 32px">
            Загрузите файл
          </span>
            <label class="input-file">
              <input :disabled="dis || off" type="file" name="file" @input="handler">
              <span style="text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">{{ butText }}</span>
            </label>
          </div>
          <div class="cont2" >
          <span style="font-weight: 600; font-size: 32px">
            Скачайте файл
          </span>
            <a :download="lol.download" :href="lol.href" @click="(event) => down ? event : event.preventDefault()">
              <button class="btn" :style="down ? null : { backgroundColor: '#eeeeee'}">Скачать</button>
            </a>
          </div>
        </div>
      </div>
    </div>
  </main>
  <notifications position="bottom center" duration="-1">
    <template #body="props">
      <div class="my-notification" :class="props.item.type === 'negative' ? 'negative' : ''">
        <div v-html="props.item.text"/>
        <button class="close" @click="() => {props.close(); off = false;}">Ок</button>
      </div>
    </template>
  </notifications>
</template>

<style scoped>
.cont3 {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 443px;
}

.my-notification {
  background-color: #A8DADC;
  margin-bottom: 15px;
  border-radius: 10px;
  border: #1d3557 solid 1px;
  color: #1d3557;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px;
  width: auto;
  gap: 5px;
  font-family: Inter, sans-serif;
}

.negative {
  background-color: #E63946;
  color: #F1FAEE;
}

main {
  background: #F1FAEE;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.box {
  width: 1240px;
  height: 720px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.title {
  font-family: "Lalezar", system-ui;
  font-size: 128px;
  color: #E63946;
  display: inline-block;
}

.page {
  width: 100%;
  display: flex;
  margin-left: 60px;
  margin-right: 60px;
  justify-content: space-between;
  align-items: start;
  font-family: "Inter", sans-serif;
  font-size: 24px;
}

.cont1 {
  background-color: #A8DADC;
  width: 525px;
  height: 443px;
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: center;
  padding-top: 33px;
}

.cont2 {
  background-color: #A8DADC;
  width: 525px;
  height: 200px;
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: center;
  color: #1d3557;
  padding-top: 33px;
  gap: 5px;
}

.form {
  display: flex;
  flex-direction: column;
  justify-content: start;
  width: 346px;
  color: #1d3557;
}

input[type="checkbox"] {
  margin-bottom: 10px;
  zoom: 1.5;
}

.input-file {
  position: relative;
  display: inline-block;
}

.btn {
  height: 65px;
  width: 405px;
  background-color: #E63946;
  border-radius: 10px;
  color: #F1FAEE;
  font-size: 24px;
  border: none;
}

.input-file span {
  position: relative;
  display: inline-block;
  cursor: pointer;
  outline: none;
  text-decoration: none;
  font-size: 24px;
  vertical-align: middle;
  color: rgb(255 255 255);
  text-align: center;
  border-radius: 10px;
  background-color: #E63946;
//line-height: 22px; height: 65px; padding: 15px 20px; box-sizing: border-box;
  border: none;
  margin: 0;
  width: 405px;
  transition: background-color 0.2s;
}

.input-file input[type=file] {
  position: absolute;
  z-index: -1;
  opacity: 0;
  display: block;
  width: 0;
  height: 0;
}

/* Focus */
.input-file input[type=file]:focus + span {
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, .25);
}

/* Hover/active */
.input-file:hover span {
  background-color: rgba(241, 89, 101, 0.95);
}

/* Disabled */
.input-file input[type=file]:disabled + span {
  background-color: #eee;
}

</style>
