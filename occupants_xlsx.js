/* Tableau des occupants pour la conciergerie, au format du fichier « Liste_occupants » de Laurent.
   Lignes : {logement, arrivee, depart, nom, personnes, tel, email, commentaire}. Nécessite ExcelJS. */
async function excelOccupants(lignes){
  const wb=new ExcelJS.Workbook();
  const feuilles=[['appartement','Appart','Tableau de reservation Appart'],['chalet','Chalet','Tableau de reservation Chalet']];
  const dateXl=s=>{const[y,m,d]=s.split('-').map(Number);return new Date(Date.UTC(y,m-1,d));};
  for(const [lg,nom,titre] of feuilles){
    const ws=wb.addWorksheet(nom);
    ws.columns=[26.4,27.2,23.2,22,22.4,36.4,23.2,75.3].map(w=>({width:w}));
    ws.mergeCells('A1:H2');
    const t=ws.getCell('A1');t.value=titre;t.font={name:'Calibri',size:20,bold:true};t.alignment={horizontal:'center',vertical:'middle'};
    const ent=['Date arrivée','Date Depart','Nom','Nombre de personnes','N° de tel','Mail',"Heure d'arrivée",'Commentaires'];
    const r4=ws.getRow(4);
    ent.forEach((h,i)=>{const c=r4.getCell(i+1);c.value=h;c.font={name:'Calibri',size:11,bold:true,color:{argb:'FFFFFFFF'}};
      c.fill={type:'pattern',pattern:'solid',fgColor:{argb:'FF2F5597'}};c.alignment={horizontal:'center',vertical:'middle'};});
    let r=5;
    lignes.filter(x=>x.logement===lg).sort((a,b)=>a.arrivee<b.arrivee?-1:1).forEach(x=>{
      const row=ws.getRow(r++);
      [dateXl(x.arrivee),dateXl(x.depart),x.nom||'',x.personnes||'',x.tel||'',x.email||'','',x.commentaire||''].forEach((v,i)=>{
        const c=row.getCell(i+1);c.value=v===''?null:v;c.font={name:'Calibri',size:11};
        c.alignment={horizontal:i===7?'left':'center',vertical:'middle',wrapText:i===7};
        if(i<2)c.numFmt='[$-40C]dddd d mmmm yyyy';});
    });
  }
  const buf=await wb.xlsx.writeBuffer();
  return new Blob([buf],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
}
