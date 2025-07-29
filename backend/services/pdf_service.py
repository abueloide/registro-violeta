from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configurar estilos personalizados para el PDF"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#6B46C1')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#4C1D95'),
            borderWidth=1,
            borderColor=colors.HexColor('#E5E7EB'),
            borderPadding=5,
            backColor=colors.HexColor('#F3F4F6')
        ))
        
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=8,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='FieldContent',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            textColor=colors.HexColor('#111827'),
            leftIndent=10
        ))
    
    def create_session_pdf(self, session_data):
        """Generar PDF de sesión terapéutica basado en el formato oficial"""
        buffer = BytesIO()
        
        try:
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Contenido del PDF
            story = []
            
            # Título principal
            title = Paragraph("SEGUIMIENTO A PROCESO TERAPÉUTICO", self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Información básica en tabla
            basic_info_data = [
                ['Sesión No.', session_data.get('sesion_no', '')],
                ['Fecha', session_data.get('fecha', '')],
                ['Código de Usuaria', session_data.get('codigo_usuaria', '')],
                ['Terapeuta', session_data.get('terapeuta', '')]
            ]
            
            basic_info_table = Table(basic_info_data, colWidths=[2*inch, 4*inch])
            basic_info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(basic_info_table)
            story.append(Spacer(1, 20))
            
            # Secciones del formato
            sections = [
                ('OBJETIVO DE LA SESIÓN', 'objetivo_sesion'),
                ('DESARROLLO DEL OBJETIVO', 'desarrollo_objetivo'),
                ('EJERCICIOS Y ACTIVIDADES DESARROLLADAS EN LA SESIÓN', 'ejercicios_actividades'),
                ('HERRAMIENTAS ENTREGADAS EN LA SESIÓN', 'herramientas_entregadas'),
                ('AVANCES EN EL PROCESO TERAPÉUTICO', 'avances_proceso_terapeutico'),
                ('CIERRE DE LA SESIÓN', 'cierre_sesion'),
                ('OBSERVACIONES', 'observaciones')
            ]
            
            for section_title, field_name in sections:
                # Título de sección
                section_header = Paragraph(section_title, self.styles['SectionHeader'])
                story.append(section_header)
                
                # Contenido de la sección
                content = session_data.get(field_name, 'No especificado')
                if content.strip():
                    # Dividir en párrafos si es muy largo
                    paragraphs = content.split('\n')
                    for para in paragraphs:
                        if para.strip():
                            content_para = Paragraph(para.strip(), self.styles['FieldContent'])
                            story.append(content_para)
                else:
                    empty_para = Paragraph("No especificado", self.styles['FieldContent'])
                    story.append(empty_para)
                
                story.append(Spacer(1, 15))
            
            # Firma del terapeuta
            story.append(Spacer(1, 20))
            firma_data = [
                ['Firma del terapeuta:', session_data.get('firma_terapeuta', '')]
            ]
            
            firma_table = Table(firma_data, colWidths=[2*inch, 4*inch])
            firma_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#F3F4F6')),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#374151')),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, 0), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(firma_table)
            
            # Footer con información de generación
            story.append(Spacer(1, 30))
            footer_text = f"Documento generado automáticamente - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            footer_para = Paragraph(footer_text, self.styles['Normal'])
            footer_para.alignment = TA_CENTER
            story.append(footer_para)
            
            # Construir el PDF
            doc.build(story)
            
            # Obtener el contenido del buffer
            pdf_content = buffer.getvalue()
            buffer.close()
            
            logger.info(f"PDF generated successfully for session {session_data.get('sesion_no', 'unknown')}")
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            buffer.close()
            return None
    
    def create_profile_pdf(self, profile_data, sessions_data=None):
        """Generar PDF de perfil de usuaria con historial de sesiones"""
        buffer = BytesIO()
        
        try:
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            story = []
            
            # Título
            title = Paragraph("PERFIL DE USUARIA", self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Información del perfil
            profile_info_data = [
                ['Código de Usuaria', profile_data.get('codigo_usuaria', '')],
                ['Edad Aproximada', profile_data.get('edad_aproximada', 'No especificada')],
                ['Situación General', profile_data.get('situacion_general', 'No especificada')],
                ['Tipo de Violencia', profile_data.get('tipo_violencia', 'No especificado')],
                ['Estado del Caso', profile_data.get('estado_caso', 'Activo')],
                ['Terapeuta Asignado', profile_data.get('terapeuta_asignado', '')],
                ['Fecha de Ingreso', profile_data.get('created_at', '')]
            ]
            
            profile_table = Table(profile_info_data, colWidths=[2*inch, 4*inch])
            profile_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(profile_table)
            story.append(Spacer(1, 20))
            
            # Notas generales si existen
            if profile_data.get('notas_generales'):
                story.append(Paragraph("NOTAS GENERALES", self.styles['SectionHeader']))
                notes_para = Paragraph(profile_data['notas_generales'], self.styles['FieldContent'])
                story.append(notes_para)
                story.append(Spacer(1, 20))
            
            # Historial de sesiones si se proporciona
            if sessions_data and len(sessions_data) > 0:
                story.append(Paragraph("HISTORIAL DE SESIONES", self.styles['SectionHeader']))
                
                sessions_headers = ['Sesión', 'Fecha', 'Tipo', 'Terapeuta']
                sessions_data_table = [sessions_headers]
                
                for session in sessions_data[:10]:  # Últimas 10 sesiones
                    row = [
                        session.get('sesion_no', ''),
                        session.get('fecha', ''),
                        session.get('tipo_sesion', 'Seguimiento'),
                        session.get('terapeuta', '')
                    ]
                    sessions_data_table.append(row)
                
                sessions_table = Table(sessions_data_table, colWidths=[1*inch, 1.5*inch, 1.5*inch, 2*inch])
                sessions_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6B46C1')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(sessions_table)
            
            # Footer
            story.append(Spacer(1, 30))
            footer_text = f"Documento generado automáticamente - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            footer_para = Paragraph(footer_text, self.styles['Normal'])
            footer_para.alignment = TA_CENTER
            story.append(footer_para)
            
            doc.build(story)
            
            pdf_content = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Profile PDF generated successfully for {profile_data.get('codigo_usuaria', 'unknown')}")
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error generating profile PDF: {e}")
            buffer.close()
            return None

# Instancia global del servicio
pdf_service = PDFService()
