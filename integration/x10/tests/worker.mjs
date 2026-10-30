import {transact} from '../../../ai/personal/x10/session.mjs';
const [runtime,base,session,id,message]=process.argv.slice(2);
console.log(JSON.stringify(transact(runtime,base,session,id,message)));
