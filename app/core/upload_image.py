import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from app.core.config import settings
import io

# Configurar Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

async def upload_image_to_cloudinary(file: UploadFile, folder: str = "products") -> str:
    """
    Sube una imagen a Cloudinary y retorna la URL
    
    Args:
        file: Archivo de imagen a subir
        folder: Carpeta en Cloudinary donde se guardará la imagen (default: "products")
    
    Returns:
        str: URL de la imagen subida
    
    Raises:
        HTTPException: Si hay un error al subir la imagen
    """
    try:
        # Validar que sea una imagen
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        # Leer el contenido del archivo
        contents = await file.read()
        
        # Subir a Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            resource_type="image",
            allowed_formats=["jpg", "jpeg", "png", "gif", "webp"]
        )
        
        # Retornar la URL segura
        return result.get("secure_url")
    
    except cloudinary.exceptions.Error as e:
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen a Cloudinary: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado al subir la imagen: {str(e)}")
    finally:
        # Asegurar que el archivo se cierra
        await file.seek(0)


async def delete_image_from_cloudinary(image_url: str) -> bool:
    """
    Elimina una imagen de Cloudinary usando su URL
    
    Args:
        image_url: URL de la imagen a eliminar
    
    Returns:
        bool: True si se eliminó correctamente
    """
    try:
        # Extraer el public_id de la URL
        # Ejemplo: https://res.cloudinary.com/cloud_name/image/upload/v123456/folder/image.jpg
        parts = image_url.split("/")
        if "upload" in parts:
            upload_index = parts.index("upload")
            # El public_id incluye la carpeta y el nombre sin extensión
            public_id_parts = parts[upload_index + 2:]  # Saltar version (v123456)
            public_id = "/".join(public_id_parts).rsplit(".", 1)[0]
            
            # Eliminar la imagen
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        return False
    except Exception as e:
        print(f"Error al eliminar imagen: {str(e)}")
        return False
