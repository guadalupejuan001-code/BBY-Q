// Storage limits are independent of the bounded page materialized in Ether.
export const VERSION='X10-Paged-Capacity-1';
export const LIMITS=Object.freeze({lessons:1048576,session_operations:1048576,input_bytes:1048576,output_bytes:1048576,page_bytes:8192});
export const B=9190000000000000000n,INPUT=B+4096n,KEY=B+2048n,RECORD=B+16384n,STAGE=B+17408n;
export const LENGTH=B+8n,TOTAL=B+12n,OFFSET=B+16n,COUNT=B+20n,REVISION=B+24n,EXISTS=B+28n,STATUS=B+29n,KEY_LENGTH=B+32n,OP=B+33n,CAPACITY=B+36n;
export const MODE=B+64n,START=B+68n,SENTENCES=B+72n,SEEN=B+76n,ENDED=B+80n,PREVIOUS=B+81n,BEFORE=B+82n,PENDING=B+83n;
export const LEGACY_BANK=9110000000000000000n,LEGACY_ROWS=LEGACY_BANK+4096n,LEGACY_CAPACITY=4096,ROW_BYTES=640;
